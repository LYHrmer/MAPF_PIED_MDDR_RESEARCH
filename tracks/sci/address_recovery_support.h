// Optional recovery contract; independent of ADDRESS types and search engines.
#pragma once
#include <algorithm>
#include <chrono>
#include <functional>
#include <fstream>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

namespace address_recovery {
using Paths = std::vector<std::vector<int>>;
using Now = std::function<long long()>;
inline long long now_ns() {
    return std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count();
}
enum class NativeEnd { UNKNOWN, FOUND, START_BLOCKED, FOCAL_DRAINED_EMPTY };
inline NativeEnd& native_end() { static NativeEnd end=NativeEnd::UNKNOWN; return end; }
enum class Stop { UNKNOWN, FOUND, DEADLINE, COST_STOP, EMPTY_UNCLASSIFIED, START_BLOCKED, FOCAL_DRAINED_EMPTY };
enum class Policy { ABANDON, RANDOM, ANCHOR };
inline const char* name(Stop stop) {
    switch(stop) {
        case Stop::UNKNOWN:return "UNKNOWN";case Stop::FOUND:return "FOUND";
        case Stop::DEADLINE:return "DEADLINE";case Stop::COST_STOP:return "COST_STOP";
        case Stop::EMPTY_UNCLASSIFIED:return "EMPTY_UNCLASSIFIED";
        case Stop::START_BLOCKED:return "START_BLOCKED";
        case Stop::FOCAL_DRAINED_EMPTY:return "FOCAL_DRAINED_EMPTY";
    }return "UNKNOWN";
}
struct Settings {
    Policy policy=Policy::ABANDON;
    int max_calls=8;
    std::mt19937 rng;
    std::ofstream trace;
};
inline Settings& settings() { static Settings s; return s; }
inline void configure(const std::string& policy, int max_calls, unsigned seed, const std::string& trace) {
    if (policy=="abandon") settings().policy=Policy::ABANDON;
    else if (policy=="random") settings().policy=Policy::RANDOM;
    else if (policy=="anchor") settings().policy=Policy::ANCHOR;
    else throw std::runtime_error("unsupported recovery policy");
    if (max_calls<1 || max_calls>8 || trace.empty() || std::ifstream(trace))
        throw std::runtime_error("invalid recovery budget/trace or existing trace");
    settings().max_calls=max_calls;
    settings().rng.seed(seed ^ 0x9e3779b9U);
    settings().trace.open(trace);
    if (!settings().trace) throw std::runtime_error("cannot open recovery trace");
}
inline Stop classify(bool empty, bool expired, NativeEnd end) {
    if (expired) return Stop::DEADLINE;
    if (!empty) return Stop::FOUND;
    if (end==NativeEnd::START_BLOCKED) return Stop::START_BLOCKED;
    if (end==NativeEnd::FOCAL_DRAINED_EMPTY) return Stop::FOCAL_DRAINED_EMPTY;
    return Stop::EMPTY_UNCLASSIFIED;
}
struct Context {
    Paths incumbent, primary; // primary has nonempty paths only for completed group prefix
    std::vector<int> order;
    size_t failed_position=0;
    int old_group_cost=0, primary_calls=0;
    Stop stop=Stop::UNKNOWN;
    long long deadline_ns=0; // min(original repair deadline, total deadline), never reset
};
struct Trace {
    std::string decision="UNSET";
    int primary_calls=0, extra_requests=0, extra_calls=0, pair_checks=0, partial_checks=0, full_checks=0;
    size_t kept=0, tail=0;
    size_t failed_position=0;
    int failed_agent=-1, prefix_cost=-1, old_failed_cost=-1, remaining_realized_budget=-1;
    bool blockers_checked=false;
    std::vector<int> blocking_prefix_agents;
    std::vector<int> original_order;
    int old_group_cost=0;
    int final_group_cost=-1;
    std::vector<Stop> extra_returns;
    long long diagnosis_ns=0, search_ns=0, validation_ns=0, total_ns=0;
    long long attempt_wall_before_trace_ns=0;
};
struct Reply { Stop stop; std::vector<int> path; bool search_executed=true; };
struct Result { bool accepted=false; Paths paths; std::vector<int> order; Trace trace; };
using Search = std::function<Reply(int,const Paths&)>;
using Validate = std::function<void(const Paths&,bool)>;
inline int at(const std::vector<int>& p,size_t t) {return p[std::min(t,p.size()-1)];}
inline bool conflict(const std::vector<int>& a,const std::vector<int>& b) {
    for(size_t t=0;t<std::max(a.size(),b.size());++t) {
        if(at(a,t)==at(b,t)) return true;
        if(t && at(a,t-1)==at(b,t) && at(b,t-1)==at(a,t)) return true;
    }
    return false;
}
inline int cost(const std::vector<int>& path) {return int(path.size())-1;}

// Normal empty means an instrumented return site, NOT a completeness theorem.
// Unknown/timeout/cost-cutoff/start-blocked do not trigger this first mechanism.
inline Result recover(const Context& c, Policy policy, int max_calls, std::mt19937& rng,
                      const Search& search,const Validate& validate,Now now=now_ns) {
    Result out; auto& tr=out.trace; tr.primary_calls=c.primary_calls;
    tr.original_order=c.order;tr.old_group_cost=c.old_group_cost;
    tr.failed_position=c.failed_position;
    if(c.failed_position<c.order.size()) tr.failed_agent=c.order[c.failed_position];
    const auto start=now();
    auto finish=[&](const std::string& why) {
        tr.decision=why;tr.total_ns=now()-start;return out;
    };
    auto check=[&](const Paths& paths,bool complete) {
        const auto begin=now();
        if(complete) ++tr.full_checks; else ++tr.partial_checks;
        validate(paths,complete);tr.validation_ns+=now()-begin;
    };
    if(c.incumbent.size()!=c.primary.size() || c.order.empty() || max_calls<1 || max_calls>8)
        throw std::runtime_error("invalid recovery context");
    std::vector<bool> member(c.incumbent.size(),false);
    int old_cost=0;
    for(int a:c.order) {
        if(a<0 || size_t(a)>=member.size() || member[a] || c.incumbent[a].empty())
            throw std::runtime_error("invalid recovery agent");
        member[a]=true;old_cost+=cost(c.incumbent[a]);
    }
    if(old_cost!=c.old_group_cost) throw std::runtime_error("incumbent group cost mismatch");
    if(now()>=c.deadline_ns) return finish("DEADLINE");
    check(c.incumbent,true); // same observation/validation protocol in all arms
    if(now()>=c.deadline_ns) return finish("DEADLINE");
    if(c.stop!=Stop::FOCAL_DRAINED_EMPTY) return finish("INELIGIBLE_STOP");
    if(c.failed_position>=c.order.size() || 2*(c.failed_position+1)<=c.order.size())
        return finish("NOT_LATE");
    const int failed=c.order[c.failed_position];
    Paths fixed=c.incumbent;
    for(int a:c.order) fixed[a].clear();
    Paths current=fixed;
    int prefix_cost=0;
    for(size_t i=0;i<c.failed_position;++i) {
        const int a=c.order[i];
        if(c.primary[a].empty()) throw std::runtime_error("missing completed prefix");
        current[a]=c.primary[a];prefix_cost+=cost(current[a]);
    }
    check(current,false);
    if(now()>=c.deadline_ns) return finish("DEADLINE");
    // Author runPP has no remaining-h per-agent cap. Only its strict realized
    // group-cost bound is used here; no old EMPTY_CAPPED certificate is imported.
    tr.prefix_cost=prefix_cost;tr.old_failed_cost=cost(c.incumbent[failed]);
    tr.remaining_realized_budget=old_cost-1-prefix_cost;
    size_t insertion=c.failed_position;
    for(size_t i=0;i<c.failed_position;++i) {
        ++tr.pair_checks;
        if(conflict(c.incumbent[failed],c.primary[c.order[i]])) {
            insertion=std::min(insertion,i);tr.blocking_prefix_agents.push_back(c.order[i]);
        }
    }
    tr.blockers_checked=true;
    if(prefix_cost+cost(c.incumbent[failed])>=old_cost) return finish("OLD_PATH_OVER_REALIZED_BUDGET");
    for(size_t a=0;a<fixed.size();++a) if(!fixed[a].empty()) {
        ++tr.pair_checks;
        if(conflict(c.incumbent[failed],fixed[a])) return finish("FIXED_PATH_BLOCKS_ANCHOR");
    }
    if(insertion==c.failed_position) return finish("NO_PREFIX_BLOCKER");
    Paths trial=fixed;
    int trial_cost=0;
    std::vector<int> new_order,tail;
    for(size_t i=0;i<insertion;++i) {
        const int a=c.order[i];trial[a]=c.primary[a];trial_cost+=cost(trial[a]);new_order.push_back(a);
    }
    trial[failed]=c.incumbent[failed];trial_cost+=cost(trial[failed]);new_order.push_back(failed);
    for(size_t i=insertion;i<c.order.size();++i) if(c.order[i]!=failed) tail.push_back(c.order[i]);
    tr.kept=insertion;tr.tail=tail.size();
    check(trial,false);
    tr.diagnosis_ns=now()-start;
    if(now()>=c.deadline_ns) return finish("DEADLINE");
    if(trial_cost>=old_cost) return finish("ANCHOR_OVER_REALIZED_BUDGET");
    // Eligibility is shared. Random is a one-shot whole-group permutation;
    // with the author's <=8 group size both methods share the same call cap.
    if(tail.size()>size_t(max_calls)) return finish("TAIL_EXCEEDS_CALL_CAP");
    // Do not give anchor a larger eligible denominator when random's complete
    // one-shot permutation cannot fit the same call allowance.
    if(c.order.size()>size_t(max_calls)) return finish("GROUP_EXCEEDS_SHARED_CALL_CAP");
    if(policy==Policy::ABANDON) return finish("ABANDON");
    if(policy==Policy::RANDOM) {
        tail=c.order;
        if(tail.size()>size_t(max_calls)) return finish("RANDOM_EXCEEDS_CALL_CAP");
        std::shuffle(tail.begin(),tail.end(),rng);trial=fixed;trial_cost=0;new_order.clear();
        tr.kept=0;tr.tail=tail.size();
    }
    for(int a:tail) {
        if(now()>=c.deadline_ns) return finish("DEADLINE");
        ++tr.extra_requests;
        const auto begin=now();const Reply reply=search(a,trial);tr.search_ns+=now()-begin;
        if(reply.search_executed) ++tr.extra_calls;
        tr.extra_returns.push_back(reply.stop);
        if(now()>=c.deadline_ns) return finish("DEADLINE");
        if(reply.stop!=Stop::FOUND || reply.path.empty()) return finish("TAIL_NOT_FOUND");
        trial[a]=reply.path;trial_cost+=cost(reply.path);new_order.push_back(a);
        if(trial_cost>=old_cost) return finish("TAIL_COST_STOP");
        check(trial,false);
        if(now()>=c.deadline_ns) return finish("DEADLINE");
    }
    check(trial,true);
    if(now()>=c.deadline_ns) return finish("DEADLINE");
    out.accepted=true;out.paths=std::move(trial);out.order=std::move(new_order);
    return finish("ACCEPTED");
}
inline void emit(const Trace& t,Stop stop,bool accepted) {
    auto& out=settings().trace;
    out << "{\"decision\":\"" <<t.decision<<"\",\"stop\":\""<<name(stop)<<"\""
        <<",\"policy\":"<<int(settings().policy)<<",\"accepted\":"<<(accepted?"true":"false")
        <<",\"old_group_cost\":"<<t.old_group_cost
        <<",\"final_group_cost\":"<<t.final_group_cost
        <<",\"primary_calls\":"<<t.primary_calls<<",\"extra_requests\":"<<t.extra_requests
        <<",\"extra_calls\":"<<t.extra_calls
        <<",\"failed_position_zero_based\":"<<t.failed_position<<",\"failed_agent\":"<<t.failed_agent
        <<",\"prefix_cost\":"<<t.prefix_cost<<",\"old_failed_cost\":"<<t.old_failed_cost
        <<",\"remaining_realized_budget\":"<<t.remaining_realized_budget
        <<",\"blockers_checked\":"<<(t.blockers_checked?"true":"false")
        <<",\"blocking_prefix_agents\":[";
    for(size_t i=0;i<t.blocking_prefix_agents.size();++i) out<<(i?",":"")<<t.blocking_prefix_agents[i];
    out << "],\"original_order\":[";
    for(size_t i=0;i<t.original_order.size();++i) out<<(i?",":"")<<t.original_order[i];
    out << "],\"extra_returns\":[";
    for(size_t i=0;i<t.extra_returns.size();++i) out<<(i?",":"")<<"\""<<name(t.extra_returns[i])<<"\"";
    out << "]"
        <<",\"kept_prefix\":"<<t.kept<<",\"tail\":"<<t.tail
        <<",\"pair_checks\":"<<t.pair_checks<<",\"partial_checks\":"<<t.partial_checks
        <<",\"full_checks\":"<<t.full_checks<<",\"diagnosis_ns\":"<<t.diagnosis_ns
        <<",\"search_ns\":"<<t.search_ns<<",\"validation_ns\":"<<t.validation_ns
        <<",\"attempt_wall_before_trace_ns\":"<<t.attempt_wall_before_trace_ns
        <<",\"recovery_wall_ns\":"<<t.total_ns<<"}\n";
    out.flush();
    if(!out) throw std::runtime_error("recovery trace output failure");
}
} // namespace address_recovery
