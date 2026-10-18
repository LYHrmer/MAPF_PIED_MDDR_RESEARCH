// Shared engineering only: cooperative wall/process-CPU deadline and cleanup reserve.
#pragma once
#include "address_adapter_support.h"
#include <ctime>
#include <exception>
#include <limits>
#include <memory>
#include <array>

namespace address_budget {
struct Deadline : std::exception {};
inline double real_wall() {
    return std::chrono::duration<double>(address_adapter::Clock::now().time_since_epoch()).count();
}
inline double real_cpu() {
    timespec value{};
    if (clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &value))
        throw std::runtime_error("budget: process CPU clock unavailable");
    return double(value.tv_sec)+double(value.tv_nsec)*1e-9;
}
using ClockFunction = double (*)();
enum class Phase { DRIVER_OTHER, PREPROCESS, LNS_OTHER, GROUP_OTHER, TOPK, BETA, WALK,
    NEIGHBOR_PREPARE, REPAIR, POST_REPAIR, FINAL_CHECK_OUTPUT, COUNT };
inline const char* phase_name(Phase phase) {
    static const char* names[]={"DRIVER_OTHER","PREPROCESS","LNS_OTHER","GROUP_OTHER","TOPK","BETA","WALK",
        "NEIGHBOR_PREPARE","REPAIR","POST_REPAIR","FINAL_CHECK_OUTPUT"};
    return names[static_cast<size_t>(phase)];
}
struct PhaseCosts {
    long long wall_ns=0,scope_entries=0,expired_calls=0,expired_samples=0,expired_sampled_wall_ns=0;
};
struct PhaseProfile {
    bool enabled=false,active=false;
    Phase current=Phase::DRIVER_OTHER;
    long long begin_ns=0,last_ns=0,window_ns=0,expired_calls=0,expired_samples=0,expired_sampled_wall_ns=0;
    long long group_calls=0,groups_formed=0,groups_no_seed=0,groups_too_small=0,groups_deadline=0;
    long long seed_calls=0,walk_calls=0,seed_zero_delay_selected=0,seed_positive_delay_selected=0;
    std::array<PhaseCosts,static_cast<size_t>(Phase::COUNT)> phases{};
};
struct SeedAdmission {
    std::string policy="all";
    long long selection_calls=0,agents_checked=0,topk_candidates=0,filtered_zero_candidates=0;
    long long retained_topk_candidates=0,empty_eligible_calls=0,deadline_calls=0,selected_calls=0;
    bool static_soc_lower_bound_reached=false;
};
struct State {
    ClockFunction wall = real_wall, cpu = real_cpu;
    bool configured=false, global_deadline=false, repair_deadline=false, search_active=false;
    bool preprocessing=false, preprocessing_fallback=false;
    bool recovery_active=false;
    double wall_stop=0, cpu_limit=0, cpu_reserve=0, local_stop=std::numeric_limits<double>::infinity();
    long group_calls=0,sipp_calls=0,sipp_deadlines=0,repair_deadlines=0,rollbacks=0;
    long attempts=0,attempt_trace_rows=0;
    long long trace_io_wall_ns=0,trace_io_cpu_ns=0;
    std::string last_stage="NONE", termination="NORMAL", last_sipp_end="NONE";
    std::string effort_mode="fixed_repairs",deadline_resource="NONE";
    int repair_cap=0;
    PhaseProfile profile;
    SeedAdmission seed_admission;
};
inline State& state() { static State s; return s; }
inline void configure_effort(const std::string& mode,int limit) {
    if((mode=="fixed_repairs"&&limit>0)||(mode=="total_budget"&&limit==0)) {
        state().effort_mode=mode;state().repair_cap=limit;return;
    }
    throw std::runtime_error("budget: effortMode and maxIterations disagree");
}
inline bool below_repair_cap(size_t stats,int limit) {
    return state().effort_mode=="total_budget"||stats<=size_t(limit);
}
inline void record_loop_exit(size_t stats,int limit) {
    auto& s=state();
    if(s.termination!="NORMAL")return;
    s.termination=s.effort_mode=="fixed_repairs"&&stats>size_t(limit)?"REPAIR_CAP":"AUTHOR_TIME_LIMIT";
}
inline void configure_seed_admission(const std::string& policy) {
    if(policy!="all"&&policy!="positive_delay")throw std::runtime_error("budget: unknown seedAdmission");
    state().seed_admission.policy=policy;
}
inline bool positive_seed_admission(){return state().seed_admission.policy=="positive_delay";}
// Read the currently committed paths on every selection; never cache labels
// across acceptance or rollback. The pinned solver computes exact distances on
// the same unit-cost graph before any seed selection can take place.
template<class Agent> inline void check_seed_delay(const Agent& agent,int delay) {
    if(!positive_seed_admission())return;
    auto& counters=state().seed_admission;++counters.agents_checked;
    const auto* planner=agent.path_planner;
    if(!planner||agent.path.empty()||agent.path.size()-1>size_t(std::numeric_limits<int>::max())
       ||planner->start_location<0||size_t(planner->start_location)>=planner->my_heuristic.size()
       ||agent.path.front().location!=planner->start_location)
        throw std::runtime_error("budget: invalid seed path or distance index");
    const int cost=int(agent.path.size())-1,h=planner->my_heuristic[planner->start_location];
    if(h<0||h>cost||delay!=cost-h)
        throw std::runtime_error("budget: invalid current-path static-distance delay");
}
inline bool retain_seed_candidate(int delay) {
    auto& counters=state().seed_admission;++counters.topk_candidates;
    if(positive_seed_admission()&&delay==0){++counters.filtered_zero_candidates;return false;}
    ++counters.retained_topk_candidates;return true;
}
inline int seed_selection_deadline(){++state().seed_admission.deadline_calls;return -1;}
inline void mark_static_soc_lower_bound() {
    state().seed_admission.static_soc_lower_bound_reached=true;
    state().termination="STATIC_SOC_BOUND";
}
inline int no_positive_seed(int total_positive) {
    if(!positive_seed_admission()||total_positive!=0)
        throw std::runtime_error("budget: empty top-k is not a certified all-zero incumbent");
    ++state().seed_admission.empty_eligible_calls;mark_static_soc_lower_bound();return -1;
}
inline void write_seed_admission(std::ostream& out) {
    const auto& c=state().seed_admission;
    out<<",\"seed_admission\":{\"schema\":\"ADDRESS_SEED_ADMISSION_V1\",\"policy\":\""<<c.policy
       <<"\",\"selection_calls\":"<<c.selection_calls<<",\"agents_checked\":"<<c.agents_checked
       <<",\"topk_candidates\":"<<c.topk_candidates<<",\"filtered_zero_candidates\":"<<c.filtered_zero_candidates
       <<",\"retained_topk_candidates\":"<<c.retained_topk_candidates<<",\"empty_eligible_calls\":"<<c.empty_eligible_calls
       <<",\"deadline_calls\":"<<c.deadline_calls<<",\"selected_calls\":"<<c.selected_calls
       <<",\"static_soc_lower_bound_reached\":"<<(c.static_soc_lower_bound_reached?"true":"false")<<"}";
}
// Profiling is optional, wall-only, and charged to the existing deadlines. It
// never consumes RNG values or adds process-CPU clock calls. Parent scopes are
// paused while a child is active: sampled expired() time is a subset, not a
// second cost added to these exclusive wall totals.
inline long long profile_wall_ns(){return static_cast<long long>(state().wall()*1e9);}
inline void configure_profile(int enabled) {
    if(enabled!=0&&enabled!=1)throw std::runtime_error("budget: phaseProfile must be 0 or 1");
    if(!enabled)return;
    auto& p=state().profile;
    if(p.enabled)throw std::runtime_error("budget: duplicate phase profile");
    p.enabled=p.active=true;p.begin_ns=p.last_ns=profile_wall_ns();
    p.phases[static_cast<size_t>(p.current)].scope_entries=1;
}
inline void profile_switch(Phase next,bool entering) {
    auto& p=state().profile;if(!p.active)return;
    const auto now=profile_wall_ns();
    p.phases[static_cast<size_t>(p.current)].wall_ns+=std::max(0LL,now-p.last_ns);
    p.last_ns=now;p.current=next;
    if(entering)++p.phases[static_cast<size_t>(next)].scope_entries;
}
struct PhaseScope {
    Phase previous;bool active;
    explicit PhaseScope(Phase phase):previous(state().profile.current),active(state().profile.active){
        if(active)profile_switch(phase,true);
    }
    PhaseScope(const PhaseScope&)=delete;PhaseScope& operator=(const PhaseScope&)=delete;
    void set(Phase phase){if(active)profile_switch(phase,true);}
    void stop(){if(active){profile_switch(previous,false);active=false;}}
    ~PhaseScope(){stop();}
};
inline void profile_finish() {
    auto& p=state().profile;if(!p.active)return;
    const auto now=profile_wall_ns();
    p.phases[static_cast<size_t>(p.current)].wall_ns+=std::max(0LL,now-p.last_ns);
    p.last_ns=now;p.window_ns=std::max(0LL,now-p.begin_ns);p.active=false;
}
enum class GroupResult { FORMED, NO_SEED, TOO_SMALL, DEADLINE };
inline bool profile_group_result(GroupResult result) {
    auto& s=state();auto& p=s.profile;
    // A seed/walk checkpoint can return through the author's no-seed or small
    // group branch. Classify that as deadline, without another budget call.
    if(result!=GroupResult::FORMED&&(s.global_deadline||s.repair_deadline))result=GroupResult::DEADLINE;
    if(p.active)switch(result){
        case GroupResult::FORMED:++p.groups_formed;break;
        case GroupResult::NO_SEED:++p.groups_no_seed;break;
        case GroupResult::TOO_SMALL:++p.groups_too_small;break;
        case GroupResult::DEADLINE:++p.groups_deadline;break;
    }
    return result==GroupResult::FORMED;
}
struct ExpiredSample {
    bool sampled=false;Phase phase=Phase::DRIVER_OTHER;long long begin_ns=0;
    ExpiredSample(){
        auto& p=state().profile;if(!p.active)return;
        phase=p.current;auto& cost=p.phases[static_cast<size_t>(phase)];
        ++cost.expired_calls;++p.expired_calls;
        sampled=p.expired_calls%1024==0;
        if(sampled)begin_ns=profile_wall_ns();
    }
    ~ExpiredSample(){
        if(!sampled)return;
        const auto elapsed=std::max(0LL,profile_wall_ns()-begin_ns);auto& p=state().profile;
        auto& cost=p.phases[static_cast<size_t>(phase)];
        ++cost.expired_samples;cost.expired_sampled_wall_ns+=elapsed;
        ++p.expired_samples;p.expired_sampled_wall_ns+=elapsed;
    }
};
inline void write_profile(std::ostream& out) {
    const auto& p=state().profile;if(!p.enabled)return;
    long long accounted=0;for(const auto& c:p.phases)accounted+=c.wall_ns;
    out<<",\"phase_profile\":{\"schema\":\"ADDRESS_PHASE_PROFILE_V1\",\"clock\":\"STEADY_WALL_NS\","
       <<"\"window\":\"CONFIGURED_TO_FINISH_BEFORE_RECEIPT\",\"window_wall_ns\":"<<p.window_ns
       <<",\"accounted_wall_ns\":"<<accounted<<",\"residual_wall_ns\":"<<p.window_ns-accounted
       <<",\"exclusive\":true,\"includes_instrumentation\":true,\"phases\":{";
    for(size_t i=0;i<p.phases.size();++i){const auto& c=p.phases[i];out<<(i?",":"")
       <<"\""<<phase_name(static_cast<Phase>(i))<<"\":{\"wall_ns\":"<<c.wall_ns<<",\"scope_entries\":"<<c.scope_entries
       <<",\"expired_calls\":"<<c.expired_calls<<",\"expired_samples\":"<<c.expired_samples
       <<",\"expired_sampled_wall_ns\":"<<c.expired_sampled_wall_ns<<"}";}
    out<<"},\"expired_sampling\":{\"sampled\":true,\"stride\":1024,\"calls\":"<<p.expired_calls
       <<",\"samples\":"<<p.expired_samples<<",\"sampled_wall_ns\":"<<p.expired_sampled_wall_ns
       <<",\"extrapolated\":false},\"counters\":{\"group_calls\":"<<p.group_calls
       <<",\"groups_formed\":"<<p.groups_formed<<",\"groups_no_seed\":"<<p.groups_no_seed
       <<",\"groups_too_small\":"<<p.groups_too_small<<",\"groups_deadline\":"<<p.groups_deadline
       <<",\"seed_calls\":"<<p.seed_calls<<",\"walk_calls\":"<<p.walk_calls
       <<",\"seed_zero_delay_selected\":"<<p.seed_zero_delay_selected
       <<",\"seed_positive_delay_selected\":"<<p.seed_positive_delay_selected<<"}}";
}
inline void configure(double cpu_limit,double cpu_reserve) {
    auto& s=state();
    if (!std::isfinite(cpu_limit)||!std::isfinite(cpu_reserve)||cpu_reserve<=0||cpu_limit<=cpu_reserve)
        throw std::runtime_error("budget: invalid process CPU reserve");
    s.cpu_limit=cpu_limit;s.cpu_reserve=cpu_reserve;
    s.wall_stop=std::chrono::duration<double>(address_adapter::state().entry.time_since_epoch()).count()
                +address_adapter::state().total_seconds-address_adapter::state().final_reserve;
    s.configured=true;
}
inline bool expired(const char* stage) {
    auto& s=state();if(!s.configured)return false;
    ExpiredSample profile_sample;
    const double wall=s.wall(),cpu=s.cpu();
    const bool wall_expired=wall>=s.wall_stop,cpu_expired=cpu>=s.cpu_limit-s.cpu_reserve;
    if(wall_expired||cpu_expired) {
        if(!s.global_deadline)s.deadline_resource=wall_expired?(cpu_expired?"WALL_AND_CPU":"WALL"):"CPU";
        s.global_deadline=true;s.termination="GLOBAL_DEADLINE";
    }
    if(s.global_deadline||wall>=s.local_stop||s.repair_deadline) {
        if(!s.repair_deadline && std::isfinite(s.local_stop))++s.repair_deadlines;
        s.repair_deadline=true;s.last_stage=stage;return true;
    }
    return false;
}
inline void checkpoint(const char* stage) { if(expired(stage))throw Deadline{}; }
inline void search_checkpoint(const char* stage) { if(state().search_active||state().recovery_active)checkpoint(stage); }
struct RecoveryScope {
    bool previous;
    RecoveryScope():previous(state().recovery_active){state().recovery_active=true;}
    ~RecoveryScope(){state().recovery_active=previous;}
};
struct Tick { long long wall,cpu; };
inline Tick tick() { return {static_cast<long long>(state().wall()*1e9),static_cast<long long>(state().cpu()*1e9)}; }
inline long long difference(long long end,long long begin){return std::max(0LL,end-begin);}
inline std::ofstream& attempt_stream(){static std::ofstream out;return out;}
inline void configure_trace(const std::string& path){
    if(path.empty())return;
    if(std::ifstream(path)||attempt_stream().is_open())throw std::runtime_error("budget: attempt trace exists");
    attempt_stream().open(path);if(!attempt_stream())throw std::runtime_error("budget: attempt trace open");
}
struct ReturnRecord {
    int position=-1,agent=-1,path_cost=-1;bool empty=true;
    std::string stop="UNKNOWN",native_end="UNKNOWN";long long wall_ns=0,cpu_ns=0;
};
struct AttemptTrace {
    long id;std::vector<int>order;int old_cost,final_cost=-1,calls=0,failed_position=-1,failed_agent=-1;
    bool complete=false,failed_attempted=false,accepted=false;
    bool blockers_checked=false,recoverability_established=false;
    std::string primary_stop="UNKNOWN",failure_site="BEFORE_CALL",recovery_decision="NONE";
    std::vector<ReturnRecord>returns;
    Tick begin,call_begin,rollback_begin;long long search_wall=0,search_cpu=0,rollback_wall=0,rollback_cpu=0;
    explicit AttemptTrace(int cost):id(++state().attempts),old_cost(cost),begin(tick()){}
    void before_call(){call_begin=tick();}
    void returned(int agent,int position,bool empty,int path_cost){
        const auto end=tick();++calls;
        ReturnRecord r;r.agent=agent;r.position=position;r.empty=empty;r.path_cost=path_cost;
        r.native_end=state().last_sipp_end;
        r.stop=expired("SIPP_RETURN")?"DEADLINE":(!empty?"FOUND":
          ((r.native_end=="START_BLOCKED"||r.native_end=="FOCAL_DRAINED_EMPTY")?r.native_end:"EMPTY_UNCLASSIFIED"));
        r.wall_ns=difference(end.wall,call_begin.wall);r.cpu_ns=difference(end.cpu,call_begin.cpu);
        search_wall+=r.wall_ns;search_cpu+=r.cpu_ns;primary_stop=r.stop;failure_site="RETURN";
        if(attempt_stream().is_open())returns.push_back(r);
    }
    void primary_done(int remaining,int position){
        complete=remaining==0;
        if(expired("PRIMARY_DONE")){primary_stop="DEADLINE";if(complete)failure_site="COMPLETE";else if(position>=calls)failure_site="BEFORE_CALL";}
        else if(complete){primary_stop="FOUND";failure_site="COMPLETE";}
        failed_position=complete?-1:position;
        failed_agent=failed_position>=0&&size_t(failed_position)<order.size()?order[failed_position]:-1;
        failed_attempted=failed_position>=0&&failed_position<calls;
    }
    void begin_rollback(){rollback_begin=tick();}
    void end_rollback(){const auto end=tick();rollback_wall=difference(end.wall,rollback_begin.wall);rollback_cpu=difference(end.cpu,rollback_begin.cpu);}
    void finish(bool ok,int cost){
        accepted=ok;final_cost=cost;
        if(!ok&&complete&&(state().repair_deadline||state().global_deadline))failure_site="FINAL_ADMISSION";
        auto& out=attempt_stream();if(!out.is_open())return;
        const auto end=tick();
        out<<"{\"schema\":\"ADDRESS_ATTEMPT_V2\",\"attempt_id\":"<<id<<",\"order\":[";
        for(size_t i=0;i<order.size();++i)out<<(i?",":"")<<order[i];
        out<<"],\"group_size\":"<<order.size()<<",\"old_group_cost\":"<<old_cost<<",\"final_group_cost\":"<<final_cost
           <<",\"primary_calls\":"<<calls<<",\"primary_returns\":[";
        for(size_t i=0;i<returns.size();++i){const auto&r=returns[i];out<<(i?",":"")
          <<"{\"position_zero_based\":"<<r.position<<",\"agent\":"<<r.agent<<",\"stop\":\""<<r.stop
          <<"\",\"native_end\":\""<<r.native_end<<"\",\"empty\":"<<(r.empty?"true":"false")
          <<",\"path_cost\":"<<r.path_cost<<",\"wall_ns\":"<<r.wall_ns<<",\"cpu_ns\":"<<r.cpu_ns<<"}";}
        out<<"],\"primary_stop\":\""<<primary_stop<<"\",\"primary_complete\":"<<(complete?"true":"false")
           <<",\"failed_position_zero_based\":"<<failed_position<<",\"failed_agent\":"<<failed_agent
           <<",\"failed_agent_attempted\":"<<(failed_attempted?"true":"false")<<",\"failure_site\":\""<<failure_site
           <<"\",\"local_deadline_reached\":"<<(state().repair_deadline?"true":"false")
           <<",\"global_deadline_reached\":"<<(state().global_deadline?"true":"false")
           <<",\"accepted\":"<<(accepted?"true":"false")<<",\"blockers_checked\":"<<(blockers_checked?"true":"false")
           <<",\"recoverability_established\":"<<(recoverability_established?"true":"false")<<",\"recovery_decision\":\""<<recovery_decision
           <<"\",\"group_calls_so_far\":"<<state().group_calls<<",\"cost\":{\"primary_search_wall_ns\":"<<search_wall
           <<",\"primary_search_cpu_ns\":"<<search_cpu<<",\"rollback_wall_ns\":"<<rollback_wall
           <<",\"rollback_cpu_ns\":"<<rollback_cpu<<",\"attempt_wall_before_trace_ns\":"<<difference(end.wall,begin.wall)
           <<",\"attempt_cpu_before_trace_ns\":"<<difference(end.cpu,begin.cpu)<<"}}\n";
        out.flush();if(!out)throw std::runtime_error("budget: attempt trace write");
        const auto wrote=tick();state().trace_io_wall_ns+=difference(wrote.wall,end.wall);
        state().trace_io_cpu_ns+=difference(wrote.cpu,end.cpu);++state().attempt_trace_rows;
    }
};
struct RepairScope {
    double previous;
    explicit RepairScope(double seconds):previous(state().local_stop) {
        state().local_stop=std::min(state().wall_stop,state().wall()+std::max(0.0,seconds));
        state().repair_deadline=false;
    }
    ~RepairScope(){state().local_stop=previous;state().repair_deadline=false;}
};
struct SearchScope {
    bool previous;
    SearchScope():previous(state().search_active){state().search_active=true;++state().sipp_calls;state().last_sipp_end="UNKNOWN";}
    ~SearchScope(){state().search_active=previous;}
};
// A pending new SIPP node is not yet owned by allNodes_table. A deadline thrown
// by dominanceCheck must delete that node before the outer catch releases stored nodes.
template<class Node,class Function> inline bool owned_dominance(Node* node,Function fn) {
    try { return fn(); } catch(const Deadline&) { delete node;throw; }
}
template<class InstanceT>
inline address_adapter::Paths prevalidate(const InstanceT& instance,size_t count) {
    const auto begin=address_adapter::Clock::now();
    auto paths=address_adapter::read_initial(count);
    address_adapter::state().initial_soc=address_adapter::check(paths,instance);
    address_adapter::state().initial_validated=true;
    address_adapter::state().initial_check_seconds=
        std::chrono::duration<double>(address_adapter::Clock::now()-begin).count();
    return paths;
}
template<class InstanceT>
inline void output_initial(const address_adapter::Paths& paths,const InstanceT& instance,const std::string& file) {
    PhaseScope profile_output(Phase::FINAL_CHECK_OUTPUT);
    const auto begin=address_adapter::Clock::now();
    address_adapter::state().final_soc=address_adapter::check(paths,instance);
    if(address_adapter::state().final_soc!=address_adapter::state().initial_soc)
        throw std::runtime_error("budget: fallback changed incumbent");
    address_adapter::state().final_validated=true;
    address_adapter::state().final_check_seconds=
        std::chrono::duration<double>(address_adapter::Clock::now()-begin).count();
    std::ofstream output(file);if(!output)throw std::runtime_error("budget: fallback output failed");
    for(size_t a=0;a<paths.size();++a) {
        output<<"Agent "<<a<<":";
        for(int loc:paths[a])output<<"("<<instance.getRowCoordinate(loc)<<","<<instance.getColCoordinate(loc)<<")->";
        output<<"\n";
    }
    output.close();if(!output)throw std::runtime_error("budget: fallback output write failed");
    state().preprocessing_fallback=true;
    state().termination="PREPROCESS_FALLBACK";
}
inline int finish() {
    profile_finish();
    const auto& a=address_adapter::state();const auto& s=state();
    const bool valid=a.initial_validated&&a.final_validated;
    const double cpu=s.cpu(),wall=address_adapter::elapsed();
    std::ofstream receipt(a.receipt_file);if(!receipt)throw std::runtime_error("budget: receipt failed");
    receipt<<std::setprecision(17)
      <<"{\"scope\":\"ADDRESS_COMMON_INITIAL_RECOMMENDED_CONFIG\",\"budget_scope\":\"SHARED_WALL_PROCESS_CPU_WITH_FINAL_RESERVE\","
      <<"\"seed\":"<<a.seed<<",\"initial_soc\":"<<a.initial_soc<<",\"final_soc\":"<<a.final_soc
      <<",\"initial_and_final_validated\":"<<(valid?"true":"false")
      <<",\"inner_wall_before_receipt_s\":"<<wall<<",\"inner_cpu_s\":"<<cpu
      <<",\"initial_check_s\":"<<a.initial_check_seconds<<",\"final_check_s\":"<<a.final_check_seconds
      <<",\"cpu_limit_s\":"<<s.cpu_limit<<",\"cpu_reserve_s\":"<<s.cpu_reserve
      <<",\"global_deadline\":"<<(s.global_deadline?"true":"false")
      <<",\"last_stage\":\""<<s.last_stage<<"\",\"termination\":\""<<s.termination
      <<"\",\"last_sipp_end\":\""<<s.last_sipp_end<<"\",\"preprocessing_fallback\":"<<(s.preprocessing_fallback?"true":"false")
      <<",\"group_calls\":"<<s.group_calls<<",\"sipp_calls\":"<<s.sipp_calls
      <<",\"sipp_deadlines\":"<<s.sipp_deadlines<<",\"repair_deadlines\":"<<s.repair_deadlines
      <<",\"rollbacks\":"<<s.rollbacks
      <<",\"effort_mode\":\""<<s.effort_mode<<"\",\"repair_cap\":"
      <<(s.effort_mode=="total_budget"?"null":std::to_string(s.repair_cap))
      <<",\"repair_attempts\":"<<s.attempts<<",\"loop_exit_reason\":\""<<s.termination
      <<"\",\"deadline_resource\":\""<<s.deadline_resource<<"\""
      <<",\"static_soc_lower_bound_reached\":"<<(s.seed_admission.static_soc_lower_bound_reached?"true":"false")
      <<",\"attempt_trace_rows\":"<<s.attempt_trace_rows<<",\"trace_io_wall_ns\":"<<s.trace_io_wall_ns
      <<",\"trace_io_cpu_ns\":"<<s.trace_io_cpu_ns
      <<",\"attempt_trace_enabled\":"<<(attempt_stream().is_open()?"true":"false")
      <<",\"reward_semantics\":\"AUTHOR_ATTEMPT_UPDATE_BEFORE_ROLLBACK\",\"external_total_budget_verified\":false";
    write_profile(receipt);write_seed_admission(receipt);receipt<<"}\n";
    receipt.close();if(!receipt)throw std::runtime_error("budget: receipt write failed");
    return valid&&address_adapter::remaining()>=0&&s.cpu()<s.cpu_limit?0:74;
}
} // namespace address_budget
