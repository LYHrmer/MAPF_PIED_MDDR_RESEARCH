// Project adaptation: transaction outcomes and seed Bernoulli memory.
// This is not DyMAB's operator selector or its signed candidate reward.
#pragma once
#include "address_budget_support.h"
#include <deque>
#include <climits>
#include <boost/uuid/detail/sha1.hpp>
#include <cstdint>
#include <set>

namespace address_reward {
struct Arm {
    long completed=0, censored=0;
    int successes=0, failures=0;
    std::deque<bool> recent;
};
struct Event {
    long id=0, repair_id=0;
    int seed=-1, group_size=0, old_task=-1, old_group=-1;
    int fresh_count=0, fresh_cost=0, candidate=-1, committed=-1;
    bool candidate_valid=false, invalid=false, censored=false, accepted=false;
    std::string outcome="UNSETTLED", stop="NOT_STARTED";
    address_budget::Tick begin;
    bool search_return_observed=false,inspection_entered=false,validation_entered=false;
    int remaining_at_search_return=-1,eligible_topk_candidates=-1;
    std::string search_loop_exit_stop="NOT_ENTERED",raw_primary_stop_before_finalization="NOT_ENTERED";
    std::string validation_stage="NOT_ENTERED",validation_result="NOT_ENTERED";
    int inspection_remaining=-1;
    std::string gate_result="NOT_ENTERED",gate_reason="NONE";
    address_budget::Tick search_return;
    bool search_censored=false,search_local_deadline=false,search_global_deadline=false;
    bool local_scope_released=false,author_observed=false,author_applied=false;
    int author_index=-1,author_old_cost=-1,author_partial_cost=-1;
    int alpha_before=-1,beta_before=-1,alpha_after=-1,beta_after=-1,alpha_settled=-1,beta_settled=-1;
    long long search_wall_ns=0,search_cpu_ns=0,search_local_remaining_ns=0;
    long long search_global_wall_remaining_ns=0,search_global_cpu_remaining_ns=0;
    std::vector<int> group_members,repair_order;
    std::string plan_before,plan_candidate;
    long revision_before=0;
    long long validation_wall_ns=0,validation_cpu_ns=0;
    long long materialization_wall_ns=0,materialization_cpu_ns=0,joint_wall_ns=0,joint_cpu_ns=0;
};
struct State {
    std::string mode="", trace, candidate_validation="all";
    std::string repair_budget="legacy",initial_plan_identity,plan_identity;
    bool execution_observations=false;
    long plan_revision=0;
    long long identity_wall_ns=0,identity_cpu_ns=0;
    int width=0;
    long started=0, settled=0, errors=0;
    long gate_skipped=0;
    long long io_wall_ns=0, io_cpu_ns=0;
    long long validation_wall_ns=0,validation_cpu_ns=0,post_search_wall_ns=0,post_search_cpu_ns=0;
    long long materialization_wall_ns=0,materialization_cpu_ns=0,joint_wall_ns=0,joint_cpu_ns=0;
    bool active=false, io_failed=false;
    Event event;
    std::vector<Arm> arms;
};
inline State& state(){static State s;return s;}
inline std::ofstream& stream(){static std::ofstream s;return s;}
inline bool author(){return state().mode=="author";}
inline bool common_budget(){return state().repair_budget=="search_then_admission";}
inline void configure(const std::string& mode,int width,int arms,const std::string& path,
                      const std::string& candidate_validation="all",
                      const std::string& repair_budget="legacy",int observations=0){
    if(!state().mode.empty() || arms<=0 || path.empty() || std::ifstream(path)
       || !((mode=="author"||mode=="cumulative")?width==0:(mode=="window"&&width>0))
       || !(candidate_validation=="all" || (candidate_validation=="acceptance_eligible"&&
            mode=="author"))
       || !(repair_budget=="legacy"||repair_budget=="search_then_admission")
       || !(observations==0||observations==1)
       || (repair_budget!="legacy"&&observations!=1)
       || (observations==1&&(!address_budget::state().cost_diagnostics||mode!="author"||
                            address_budget::attempt_stream().is_open())))
        throw std::runtime_error("reward: invalid/repeated configuration or existing trace");
    stream().open(path);if(!stream())throw std::runtime_error("reward: trace open failed");
    state().mode=mode;state().width=width;state().trace=path;state().arms.resize(arms);
    state().candidate_validation=candidate_validation;
    state().repair_budget=repair_budget;state().execution_observations=observations==1;
}
inline Event& pending(){
    if(!state().active)throw std::runtime_error("reward: no pending selection / duplicate settlement");
    return state().event;
}
inline std::string nullable(int value){return value<0?"null":std::to_string(value);}
// A content fingerprint within the manifest-bound map/model, not a safety
// certificate. SHA1 uses the existing Boost dependency. Canonical words are
// unsigned 32-bit little endian: number of paths, then each length and cells.
inline std::string path_identity(const address_adapter::Paths& paths){
    const auto start=address_budget::tick();boost::uuids::detail::sha1 hash;
    auto word=[&](size_t value){
        if(value>UINT32_MAX)throw std::runtime_error("reward: identity word overflow");
        unsigned char bytes[4];for(int j=0;j<4;++j)bytes[j]=static_cast<unsigned char>(value>>(8*j));
        hash.process_bytes(bytes,4);
    };
    word(paths.size());
    for(const auto& path:paths){word(path.size());for(int cell:path){
        if(cell<0)throw std::runtime_error("reward: negative identity cell");word(size_t(cell));
    }}
    unsigned int words[5];hash.get_digest(words);std::string value;
    const char* hex="0123456789abcdef";
    for(auto x:words)for(int shift=28;shift>=0;shift-=4)value.push_back(hex[(x>>shift)&15]);
    const auto end=address_budget::tick();state().identity_wall_ns+=address_budget::difference(end.wall,start.wall);
    state().identity_cpu_ns+=address_budget::difference(end.cpu,start.cpu);return value;
}
inline void initialize_plan_identity(const address_adapter::Paths& paths){
    if(!state().execution_observations)return;
    if(!state().initial_plan_identity.empty())throw std::runtime_error("reward: repeated initial identity");
    state().initial_plan_identity=state().plan_identity=path_identity(paths);
}
inline void begin(int old_task){
    auto& s=state();
    if(s.mode.empty()||s.active||old_task<0)throw std::runtime_error("reward: invalid begin");
    s.event=Event{};s.event.id=++s.started;s.event.old_task=old_task;
    if(s.execution_observations){
        if(s.plan_identity.empty())throw std::runtime_error("reward: initial plan identity missing");
        s.event.plan_before=s.plan_identity;s.event.revision_before=s.plan_revision;
    }
    if(address_budget::state().cost_diagnostics)address_budget::state().event_deadlines={};
    s.event.begin=address_budget::tick();s.active=true;
}
inline void seed_pool_completed(int count){
    if(!address_budget::state().cost_diagnostics)return;
    auto&e=pending();if(count<0||e.eligible_topk_candidates>=0)throw std::runtime_error("reward: repeated seed pool");
    e.eligible_topk_candidates=count;
}
inline void search_returned(const std::string& stop,int remaining){
    // The opt-in contract snapshots after PRIMARY_DONE, whose checkpoint may
    // itself observe expiry. Legacy keeps its earlier observation location.
    if(!address_budget::state().cost_diagnostics)return;
    auto&e=pending();if(e.search_return_observed||remaining<0)throw std::runtime_error("reward: repeated search return");
    e.search_return=address_budget::tick();e.search_return_observed=true;
    e.raw_primary_stop_before_finalization=stop;e.remaining_at_search_return=remaining;
    e.search_loop_exit_stop=(address_budget::state().global_deadline||address_budget::state().repair_deadline)?
        "DEADLINE":remaining==0?"COMPLETE":stop;
    if(state().execution_observations){
        const auto& b=address_budget::state();
        e.search_censored=b.repair_deadline||b.global_deadline;
        e.search_local_deadline=b.event_deadlines.local.seen;
        e.search_global_deadline=b.global_deadline;
        e.search_wall_ns=e.search_return.wall;e.search_cpu_ns=e.search_return.cpu;
        e.search_local_remaining_ns=static_cast<long long>(b.local_stop*1e9)-e.search_wall_ns;
        e.search_global_wall_remaining_ns=static_cast<long long>(b.wall_stop*1e9)-e.search_wall_ns;
        e.search_global_cpu_remaining_ns=static_cast<long long>((b.cpu_limit-b.cpu_reserve)*1e9)-e.search_cpu_ns;
    }
}
inline void enter_admission(){
    if(!common_budget())return;
    auto& e=pending();auto& b=address_budget::state();
    if(!e.search_return_observed||e.local_scope_released)throw std::runtime_error("reward: admission transition");
    e.search_censored=e.search_censored||b.repair_deadline||b.global_deadline;
    e.search_local_deadline=e.search_local_deadline||b.event_deadlines.local.seen;
    e.search_global_deadline=e.search_global_deadline||b.global_deadline;
    e.local_scope_released=true;e.censored=e.censored||e.search_censored;
    b.local_stop=std::numeric_limits<double>::infinity();
    // Keep global expiry sticky. Search-local censoring remains on the event;
    // releasing the local clock must never resurrect an unfinished candidate.
    b.repair_deadline=b.global_deadline;
}
inline void observe_group(const std::vector<int>& members){
    if(!state().execution_observations)return;
    auto& e=pending();if(int(members.size())!=e.group_size||!e.group_members.empty())
        throw std::runtime_error("reward: group observation mismatch");
    e.group_members=members;
}
inline void observe_order(const std::vector<int>& order){
    if(!state().execution_observations)return;
    auto& e=pending();std::set<int> members(e.group_members.begin(),e.group_members.end()),actual(order.begin(),order.end());
    if(!e.repair_order.empty()||order.size()!=e.group_members.size()||actual!=members||actual.size()!=order.size())
        throw std::runtime_error("reward: repair order mismatch");
    e.repair_order=order;
}
inline void author_before(int index,int old_cost,int partial_cost,const std::vector<int>& alpha,
                          const std::vector<int>& beta,bool applied){
    if(!state().execution_observations)return;
    auto& e=pending();if(e.author_observed||e.seed<0||alpha.size()!=state().arms.size()||beta.size()!=alpha.size())
        throw std::runtime_error("reward: author observation mismatch");
    if(applied&&index!=e.seed)throw std::runtime_error("reward: author updated different seed");
    e.author_observed=true;e.author_applied=applied;e.author_index=index;
    e.author_old_cost=old_cost;e.author_partial_cost=partial_cost;
    e.alpha_before=alpha.at(e.seed);e.beta_before=beta.at(e.seed);
}
inline void author_after(const std::vector<int>& alpha,const std::vector<int>& beta){
    if(!state().execution_observations)return;
    auto& e=pending();if(!e.author_observed||e.alpha_after!=-1)throw std::runtime_error("reward: author update missing/repeated");
    e.alpha_after=alpha.at(e.seed);e.beta_after=beta.at(e.seed);
    const bool success=e.author_old_cost>e.author_partial_cost;
    if(e.alpha_after!=e.alpha_before+int(e.author_applied&&success)||
       e.beta_after!=e.beta_before+int(e.author_applied&&!success))
        throw std::runtime_error("reward: actual author posterior delta mismatch");
}
struct CandidateValidationCost {
    bool enabled;address_budget::Tick begin,last;int phase=0;
    CandidateValidationCost():enabled(address_budget::state().cost_diagnostics){
        if(!enabled)return;
        auto&e=pending();if(e.validation_entered)throw std::runtime_error("reward: nested/repeated validation");
        e.validation_entered=true;begin=last=address_budget::tick();
    }
    void account(address_budget::Tick end){
        auto&e=pending();
        const auto wall=address_budget::difference(end.wall,last.wall),cpu=address_budget::difference(end.cpu,last.cpu);
        if(phase==1){e.materialization_wall_ns+=wall;e.materialization_cpu_ns+=cpu;}
        if(phase==2){e.joint_wall_ns+=wall;e.joint_cpu_ns+=cpu;}
        last=end;
    }
    void enter(int next){if(enabled){account(address_budget::tick());phase=next;}}
    ~CandidateValidationCost(){
        if(!enabled)return;
        const auto end=address_budget::tick();account(end);auto&e=pending();
        e.validation_wall_ns=address_budget::difference(end.wall,begin.wall);
        e.validation_cpu_ns=address_budget::difference(end.cpu,begin.cpu);
    }
};
inline void bind_seed(int id){
    auto& e=pending();
    if(e.seed!=-1 || id<0 || size_t(id)>=state().arms.size())throw std::runtime_error("reward: invalid/repeated seed");
    e.seed=id;
}
inline void group(int size,int old_cost){
    auto& e=pending();
    if(e.old_group!=-1||size<=0||old_cost<0||old_cost>e.old_task)throw std::runtime_error("reward: group mismatch");
    e.group_size=size;e.old_group=old_cost;e.repair_id=address_budget::state().attempts;
}
inline void found(int cost){
    auto& e=pending();
    if(e.old_group<0||cost<0||e.fresh_count>=e.group_size||cost>INT_MAX-e.fresh_cost)
        throw std::runtime_error("reward: invalid fresh path");
    ++e.fresh_count;e.fresh_cost+=cost;
}

// Validate the whole joint candidate, including unchanged vehicles and permanent
// goals. All fresh paths must exist; an old path remaining in agents is not one.
template<class Agents,class Instance>
inline void inspect_candidate(const Agents& agents,const Instance& instance,int remaining_agents){
    auto& e=pending();
    const bool diagnostic=address_budget::state().cost_diagnostics;
    const bool gated=state().candidate_validation=="acceptance_eligible";
    if(gated){
        if(remaining_agents<0||remaining_agents>e.group_size||e.inspection_remaining>=0)
            throw std::runtime_error("reward: invalid/repeated acceptance inspection");
        e.inspection_remaining=remaining_agents;e.gate_result="INCOMPLETE_SKIPPED";
    }
    if(diagnostic){e.inspection_entered=true;e.validation_result="INCOMPLETE_SKIPPED";}
    if(common_budget()&&e.search_censored){
        e.gate_result="SEARCH_CENSORED";
        if(diagnostic){e.validation_stage="SEARCH_CENSORED";e.validation_result="SEARCH_CENSORED";}
        return;
    }
    if(e.fresh_count!=e.group_size)return;
    CandidateValidationCost validation_cost;
    try {
        if(diagnostic)e.validation_stage="ENTRY_CHECKPOINT";
        address_budget::checkpoint(diagnostic?"REWARD_VALIDATION_ENTRY":"REWARD_VALIDATION");
        // Reuse the actual acceptance prerequisites, not a diagnostic stop label.
        // Keep the entry deadline check above and the original author update,
        // rollback, settlement and final whole-plan check after this function.
        if(gated&&(remaining_agents!=0||e.fresh_cost>e.old_group)){
            e.gate_result="SKIPPED_ACCEPTANCE_INELIGIBLE";
            e.gate_reason=remaining_agents!=0?"REMAINING_AGENTS":"COST_EXCEEDS_OLD";
            ++state().gate_skipped;
            if(diagnostic){e.validation_stage="ACCEPTANCE_GATE";e.validation_result=e.gate_result;}
            return; // candidate/candidate_reward remain unknown, not validated.
        }
        validation_cost.enter(1);
        if(diagnostic)e.validation_stage="PATH_MATERIALIZATION";
        address_adapter::Paths paths;
        for(const auto& a:agents){
            paths.emplace_back();
            for(const auto& step:a.path){address_budget::checkpoint(diagnostic?"REWARD_VALIDATION_PATHS":"REWARD_VALIDATION");paths.back().push_back(step.location);}
        }
        std::vector<bool> blocked(instance.map_size);
        if(diagnostic)e.validation_stage="MAP_MATERIALIZATION";
        for(int i=0;i<instance.map_size;++i){address_budget::checkpoint(diagnostic?"REWARD_VALIDATION_MAP":"REWARD_VALIDATION");blocked[i]=instance.isObstacle(i);}
        if(diagnostic)e.validation_stage="JOINT_CHECK";
        validation_cost.enter(2);
        const int total=address_adapter::validate(paths,instance.num_of_rows,instance.num_of_cols,
            blocked,instance.getStarts(),instance.getGoals(),[diagnostic](){address_budget::checkpoint(diagnostic?"REWARD_VALIDATION_JOINT":"REWARD_VALIDATION");});
        validation_cost.enter(0);
        if(static_cast<long long>(e.old_task)-e.old_group+e.fresh_cost!=total)
            throw std::runtime_error("reward: candidate SOC mismatch");
        if(state().execution_observations&&remaining_agents==0&&e.fresh_cost<=e.old_group)
            e.plan_candidate=path_identity(paths);
        if(diagnostic)e.validation_stage="FINAL_CHECKPOINT";
        address_budget::checkpoint("REWARD_VALIDATION_DONE");
        e.candidate=e.fresh_cost;e.candidate_valid=true;
        if(gated)e.gate_result="VALIDATED";
        if(diagnostic){e.validation_stage="COMPLETE";e.validation_result="VALIDATED";}
    } catch(const address_budget::Deadline&){e.censored=true;if(gated)e.gate_result="DEADLINE";if(diagnostic)e.validation_result="DEADLINE";}
      catch(const std::runtime_error&){e.invalid=true;if(gated)e.gate_result="INVALID";if(diagnostic)e.validation_result="INVALID";}
}
inline bool admissible(){return pending().candidate_valid&&!pending().invalid&&!pending().censored;}

inline void write_vector(std::ostream& out,const std::vector<int>& values){
    out<<"[";for(size_t i=0;i<values.size();++i)out<<(i?",":"")<<values[i];out<<"]";
}
inline void write_execution_observations(std::ostream& out){
    if(!state().execution_observations)return;
    const auto& e=pending();const auto& s=state();
    out<<",\"execution_observations\":{\"schema\":\"ADDRESS_EXECUTION_OBSERVATIONS_V1\""
       <<",\"repair_budget_contract\":\""<<s.repair_budget<<"\",\"group_members\":";
    write_vector(out,e.group_members);out<<",\"repair_order\":";write_vector(out,e.repair_order);
    out<<",\"search_return\":";
    if(!e.search_return_observed)out<<"null";
    else out<<"{\"wall_ns\":"<<e.search_wall_ns<<",\"cpu_ns\":"<<e.search_cpu_ns
       <<",\"local_remaining_wall_ns\":"<<e.search_local_remaining_ns
       <<",\"global_remaining_wall_ns\":"<<e.search_global_wall_remaining_ns
       <<",\"global_remaining_cpu_ns\":"<<e.search_global_cpu_remaining_ns
       <<",\"local_deadline_observed\":"<<(e.search_local_deadline?"true":"false")
       <<",\"global_deadline_observed\":"<<(e.search_global_deadline?"true":"false")
       <<",\"search_censored\":"<<(e.search_censored?"true":"false")
       <<",\"local_scope_released\":"<<(e.local_scope_released?"true":"false")<<"}";
    out<<",\"author_update\":";
    if(!e.author_observed)out<<"null";
    else out<<"{\"index\":"<<nullable(e.author_index)<<",\"applied\":"<<(e.author_applied?"true":"false")
       <<",\"old_subset_soc\":"<<e.author_old_cost<<",\"partial_subset_soc\":"<<e.author_partial_cost
       <<",\"positive_predicate\":"<<(e.author_old_cost>e.author_partial_cost?"true":"false")
       <<",\"alpha_before\":"<<e.alpha_before<<",\"beta_before\":"<<e.beta_before
       <<",\"alpha_after\":"<<e.alpha_after<<",\"beta_after\":"<<e.beta_after<<"}";
    out<<",\"selected_posterior_after_settlement\":";
    if(e.seed<0)out<<"null";else out<<"{\"alpha\":"<<e.alpha_settled<<",\"beta\":"<<e.beta_settled<<"}";
    out<<",\"plan_identity\":{\"encoding\":\"NATIVE_PATHS_U32LE_SHA1_V1\""
       <<",\"scope\":\"WITHIN_MANIFEST_BOUND_MODEL_NOT_SAFETY_CERTIFICATE\""
       <<",\"before_sha1\":\""<<e.plan_before<<"\",\"after_sha1\":\""<<s.plan_identity
       <<"\",\"revision_before\":"<<e.revision_before<<",\"revision_after\":"<<s.plan_revision<<"}}";
}

// One completed event, one memory update. Unselected, censored and invalid
// events are logged and charged but never inserted as zero-reward samples.
inline void learn(Event& e,std::vector<int>& alpha,std::vector<int>& beta){
    if(e.seed<0)return;
    auto& a=state().arms.at(e.seed);
    if(e.censored){++a.censored;return;}
    if(e.invalid)return;
    if(alpha.size()!=state().arms.size()||beta.size()!=state().arms.size())
        throw std::runtime_error("reward: posterior dimensions");
    const bool improved=e.old_task>e.committed;
    if(a.successes==INT_MAX-1||a.failures==INT_MAX-1)throw std::runtime_error("reward: count overflow");
    ++a.completed;
    if(improved)++a.successes;else ++a.failures;
    if(state().mode=="window"){
        a.recent.push_back(improved);
        if(a.recent.size()>size_t(state().width)){
            if(a.recent.front())--a.successes;else --a.failures;
            a.recent.pop_front();
        }
    }
    if(!author()){alpha[e.seed]=1+a.successes;beta[e.seed]=1+a.failures;}
}
inline void emit(){
    auto& s=state();auto& e=pending();const auto end=address_budget::tick();auto& out=stream();
    const bool eligible=e.seed>=0&&!e.censored&&!e.invalid;
    out<<"{\"schema\":\"ADDRESS_REWARD_V1\",\"selection_id\":"<<e.id
       <<",\"repair_attempt_id\":"<<(e.repair_id?std::to_string(e.repair_id):"null")
       <<",\"operator_id\":0,\"seed_id\":"<<nullable(e.seed)<<",\"group_size\":"<<e.group_size
       <<",\"outcome\":\""<<e.outcome<<"\",\"stop\":\""<<e.stop<<"\",\"old_task_soc\":"<<e.old_task
       <<",\"old_subset_soc\":"<<nullable(e.old_group)<<",\"fresh_paths\":"<<e.fresh_count
       <<",\"candidate_validated\":"<<(e.candidate_valid?"true":"false")
       <<",\"candidate_subset_soc\":"<<nullable(e.candidate)<<",\"candidate_reward\":"
       <<(e.candidate_valid?std::to_string(e.old_group-e.candidate):"null")
       <<",\"committed_task_soc\":"<<nullable(e.committed)<<",\"committed_gain\":"
       <<(e.committed>=0?std::to_string(e.old_task-e.committed):"null")
       <<",\"accepted\":"<<(e.accepted?"true":"false")<<",\"censored\":"<<(e.censored?"true":"false")
       <<",\"local_deadline\":"<<((common_budget()?e.search_local_deadline:address_budget::state().repair_deadline)?"true":"false")
       <<",\"global_deadline\":"<<(address_budget::state().global_deadline?"true":"false")
       <<",\"deadline_stage\":\""<<(e.censored?address_budget::state().last_stage:"NONE")
       <<"\",\"deadline_resource\":\""<<(e.censored?address_budget::state().deadline_resource:"NONE")<<"\""
       <<",\"memory_eligible\":"<<(eligible?"true":"false")<<",\"bernoulli_reward\":"
       <<(eligible?(e.old_task>e.committed?"1":"0"):"null")
       <<",\"selection_wall_before_log_ns\":"<<address_budget::difference(end.wall,e.begin.wall)
       <<",\"selection_cpu_before_log_ns\":"<<address_budget::difference(end.cpu,e.begin.cpu);
    if(s.candidate_validation!="all")
        out<<",\"candidate_validation_policy\":{\"schema\":\"ADDRESS_CANDIDATE_VALIDATION_V1\""
           <<",\"mode\":\""<<s.candidate_validation<<"\",\"result\":\""<<e.gate_result
           <<"\",\"skip_reason\":\""<<e.gate_reason<<"\",\"remaining_agents\":"<<nullable(e.inspection_remaining)
           <<",\"fresh_cost_sum_unvalidated\":"<<(e.repair_id?std::to_string(e.fresh_cost):"null")<<"}";
    if(address_budget::state().cost_diagnostics){
        const auto post_wall=e.search_return_observed?address_budget::difference(end.wall,e.search_return.wall):0;
        const auto post_cpu=e.search_return_observed?address_budget::difference(end.cpu,e.search_return.cpu):0;
        if(e.validation_wall_ns>post_wall||e.validation_cpu_ns>post_cpu)
            throw std::runtime_error("reward: validation outside post-search interval");
        s.validation_wall_ns+=e.validation_wall_ns;s.validation_cpu_ns+=e.validation_cpu_ns;
        s.materialization_wall_ns+=e.materialization_wall_ns;s.materialization_cpu_ns+=e.materialization_cpu_ns;
        s.joint_wall_ns+=e.joint_wall_ns;s.joint_cpu_ns+=e.joint_cpu_ns;
        s.post_search_wall_ns+=post_wall;s.post_search_cpu_ns+=post_cpu;
        out<<",\"cost_diagnostics\":{\"schema\":\"ADDRESS_REWARD_COST_V1\",";
        address_budget::write_deadline_observations(out,address_budget::state().event_deadlines);
        out<<",\"search_return_observed\":"<<(e.search_return_observed?"true":"false")
           <<",\"search_loop_exit_stop\":\""<<e.search_loop_exit_stop<<"\",\"remaining_at_search_return\":"<<nullable(e.remaining_at_search_return)
           <<",\"raw_primary_stop_before_finalization\":\""<<e.raw_primary_stop_before_finalization<<"\""
           <<",\"seed_pool_completed\":"<<(e.eligible_topk_candidates>=0?"true":"false")
           <<",\"eligible_topk_candidates\":"<<nullable(e.eligible_topk_candidates)
           <<",\"inspection_entered\":"<<(e.inspection_entered?"true":"false")
           <<",\"validation_entered\":"<<(e.validation_entered?"true":"false")
           <<",\"validation_last_stage\":\""<<e.validation_stage<<"\",\"validation_result\":\""<<e.validation_result<<"\""
           <<",\"candidate_validation_wall_ns\":"<<e.validation_wall_ns<<",\"candidate_validation_cpu_ns\":"<<e.validation_cpu_ns
           <<",\"candidate_materialization_wall_ns\":"<<e.materialization_wall_ns<<",\"candidate_materialization_cpu_ns\":"<<e.materialization_cpu_ns
           <<",\"candidate_joint_check_wall_ns\":"<<e.joint_wall_ns<<",\"candidate_joint_check_cpu_ns\":"<<e.joint_cpu_ns
           <<",\"candidate_validation_other_wall_ns\":"<<e.validation_wall_ns-e.materialization_wall_ns-e.joint_wall_ns
           <<",\"candidate_validation_other_cpu_ns\":"<<e.validation_cpu_ns-e.materialization_cpu_ns-e.joint_cpu_ns
           <<",\"post_search_through_settlement_wall_ns\":"<<post_wall<<",\"post_search_through_settlement_cpu_ns\":"<<post_cpu
           <<",\"post_search_other_wall_ns\":"<<post_wall-e.validation_wall_ns
           <<",\"post_search_other_cpu_ns\":"<<post_cpu-e.validation_cpu_ns
           <<",\"cost_scope\":\"VALIDATION_SUBSET_OF_POST_SEARCH_SUBSET_OF_SELECTION_BEFORE_LOG\"}";
    }
    write_execution_observations(out);
    out<<"}\n";
    out.flush();if(!out)throw std::runtime_error("reward: event output failed");
    const auto wrote=address_budget::tick();s.io_wall_ns+=address_budget::difference(wrote.wall,end.wall);
    s.io_cpu_ns+=address_budget::difference(wrote.cpu,end.cpu);++s.settled;s.active=false;
}
inline void settle(bool accepted,int committed_subset,const std::string& stop,
                   std::vector<int>& alpha,std::vector<int>& beta){
    auto& e=pending();e.stop=stop;e.accepted=accepted;
    e.censored=e.censored||address_budget::state().global_deadline||address_budget::state().repair_deadline;
    if(e.old_group<0 || committed_subset<0 || committed_subset>e.old_group
       || (accepted&&(!admissible()||e.censored||committed_subset!=e.candidate))
       || (!accepted&&committed_subset!=e.old_group))throw std::runtime_error("reward: commit mismatch");
    e.committed=e.old_task-e.old_group+committed_subset;
    e.outcome=e.invalid?"INVALID_CANDIDATE":e.censored?"CENSORED":accepted?"ACCEPTED":"ROLLED_BACK";
    const bool invalid=e.invalid;
    if(invalid)++state().errors;
    learn(e,alpha,beta);
    if(state().execution_observations){
        if(accepted){
            if(e.plan_candidate.empty())throw std::runtime_error("reward: accepted plan identity missing");
            state().plan_identity=e.plan_candidate;++state().plan_revision;
        }
        if(e.seed>=0){e.alpha_settled=alpha.at(e.seed);e.beta_settled=beta.at(e.seed);}
    }
    emit();
    if(invalid)throw std::runtime_error("reward: invalid joint candidate; rolled back");
}
inline void no_repair(const std::string& why,std::vector<int>& alpha,std::vector<int>& beta){
    auto& e=pending();
    if(e.old_group>=0)throw std::runtime_error("reward: no-repair after group deletion");
    e.stop=why;e.committed=e.old_task;
    e.censored=address_budget::state().global_deadline||address_budget::state().repair_deadline;
    e.outcome=e.censored?"CENSORED":"NO_GROUP";learn(e,alpha,beta);
    if(state().execution_observations&&e.seed>=0){e.alpha_settled=alpha.at(e.seed);e.beta_settled=beta.at(e.seed);}
    emit();
}
struct SelectionScope {
    explicit SelectionScope(int old_task){begin(old_task);}
    SelectionScope(const SelectionScope&)=delete;
    SelectionScope& operator=(const SelectionScope&)=delete;
    ~SelectionScope(){
        if(!state().active)return;
        // No implicit success/zero reward on exceptions or missed return hooks.
        ++state().errors;pending().invalid=true;pending().committed=-1;pending().outcome="UNSETTLED_ERROR";
        try{emit();}catch(...){state().io_failed=true;state().active=false;}
    }
};
inline void summary(std::ostream& out){
    const auto& s=state();
    if(s.active||s.started!=s.settled||s.errors||s.io_failed)throw std::runtime_error("reward: incomplete/error ledger");
    out<<",\"reward_contract\":{\"schema\":\"ADDRESS_REWARD_V1\",\"memory\":\""<<s.mode
       <<"\",\"decision\":\"VEHICLE_SEED_PROJECT_ADAPTATION\",\"reward\":\"COMMITTED_GAIN_POSITIVE_BERNOULLI\""
       <<",\"posterior_rule\":\""<<(author()?"AUTHOR_ATTEMPT_BEFORE_ROLLBACK":"POST_COMMIT_BERNOULLI")<<"\""
       <<",\"window\":"<<s.width<<",\"prior_alpha\":1,\"prior_beta\":1"
       <<",\"selections\":"<<s.started<<",\"settlements\":"<<s.settled
       <<",\"log_wall_ns\":"<<s.io_wall_ns<<",\"log_cpu_ns\":"<<s.io_cpu_ns<<",\"arms\":[";
    for(size_t i=0;i<s.arms.size();++i){const auto& a=s.arms[i];out<<(i?",":"")
        <<"{\"seed\":"<<i<<",\"completed\":"<<a.completed<<",\"censored\":"<<a.censored
        <<",\"retained_successes\":"<<a.successes<<",\"retained_failures\":"<<a.failures<<"}";}
    out<<"]";
    if(s.execution_observations)
        out<<",\"execution_observations\":{\"schema\":\"ADDRESS_EXECUTION_OBSERVATIONS_V1\""
           <<",\"repair_budget_contract\":\""<<s.repair_budget
           <<"\",\"initial_plan_sha1\":\""<<s.initial_plan_identity
           <<"\",\"final_plan_sha1\":\""<<s.plan_identity<<"\",\"final_revision\":"<<s.plan_revision
           <<",\"identity_wall_ns\":"<<s.identity_wall_ns<<",\"identity_cpu_ns\":"<<s.identity_cpu_ns
           <<",\"identity_cost_is_nested_in_recorded_total\":true}";
    if(s.candidate_validation!="all")
        out<<",\"candidate_validation_policy\":{\"schema\":\"ADDRESS_CANDIDATE_VALIDATION_V1\""
           <<",\"mode\":\""<<s.candidate_validation<<"\",\"skipped_acceptance_ineligible\":"<<s.gate_skipped<<"}";
    if(address_budget::state().cost_diagnostics)
        out<<",\"cost_diagnostics\":{\"schema\":\"ADDRESS_REWARD_COST_V1\""
           <<",\"candidate_validation_wall_ns\":"<<s.validation_wall_ns<<",\"candidate_validation_cpu_ns\":"<<s.validation_cpu_ns
           <<",\"candidate_materialization_wall_ns\":"<<s.materialization_wall_ns<<",\"candidate_materialization_cpu_ns\":"<<s.materialization_cpu_ns
           <<",\"candidate_joint_check_wall_ns\":"<<s.joint_wall_ns<<",\"candidate_joint_check_cpu_ns\":"<<s.joint_cpu_ns
           <<",\"candidate_validation_other_wall_ns\":"<<s.validation_wall_ns-s.materialization_wall_ns-s.joint_wall_ns
           <<",\"candidate_validation_other_cpu_ns\":"<<s.validation_cpu_ns-s.materialization_cpu_ns-s.joint_cpu_ns
           <<",\"post_search_through_settlement_wall_ns\":"<<s.post_search_wall_ns
           <<",\"post_search_through_settlement_cpu_ns\":"<<s.post_search_cpu_ns<<"}";
    out<<"}";
}
} // namespace address_reward
