// Project adaptation: transaction outcomes and seed Bernoulli memory.
// This is not DyMAB's operator selector or its signed candidate reward.
#pragma once
#include "address_budget_support.h"
#include <deque>
#include <climits>

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
    address_budget::Tick search_return;
    long long validation_wall_ns=0,validation_cpu_ns=0;
    long long materialization_wall_ns=0,materialization_cpu_ns=0,joint_wall_ns=0,joint_cpu_ns=0;
};
struct State {
    std::string mode="", trace;
    int width=0;
    long started=0, settled=0, errors=0;
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
inline void configure(const std::string& mode,int width,int arms,const std::string& path){
    if(!state().mode.empty() || arms<=0 || path.empty() || std::ifstream(path)
       || !((mode=="author"||mode=="cumulative")?width==0:(mode=="window"&&width>0)))
        throw std::runtime_error("reward: invalid/repeated configuration or existing trace");
    stream().open(path);if(!stream())throw std::runtime_error("reward: trace open failed");
    state().mode=mode;state().width=width;state().trace=path;state().arms.resize(arms);
}
inline Event& pending(){
    if(!state().active)throw std::runtime_error("reward: no pending selection / duplicate settlement");
    return state().event;
}
inline std::string nullable(int value){return value<0?"null":std::to_string(value);}
inline void begin(int old_task){
    auto& s=state();
    if(s.mode.empty()||s.active||old_task<0)throw std::runtime_error("reward: invalid begin");
    s.event=Event{};s.event.id=++s.started;s.event.old_task=old_task;
    if(address_budget::state().cost_diagnostics)address_budget::state().event_deadlines={};
    s.event.begin=address_budget::tick();s.active=true;
}
inline void seed_pool_completed(int count){
    if(!address_budget::state().cost_diagnostics)return;
    auto&e=pending();if(count<0||e.eligible_topk_candidates>=0)throw std::runtime_error("reward: repeated seed pool");
    e.eligible_topk_candidates=count;
}
inline void search_returned(const std::string& stop,int remaining){
    if(!address_budget::state().cost_diagnostics)return;
    auto&e=pending();if(e.search_return_observed||remaining<0)throw std::runtime_error("reward: repeated search return");
    e.search_return=address_budget::tick();e.search_return_observed=true;
    e.raw_primary_stop_before_finalization=stop;e.remaining_at_search_return=remaining;
    e.search_loop_exit_stop=(address_budget::state().global_deadline||address_budget::state().repair_deadline)?
        "DEADLINE":remaining==0?"COMPLETE":stop;
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
inline void inspect_candidate(const Agents& agents,const Instance& instance){
    auto& e=pending();
    const bool diagnostic=address_budget::state().cost_diagnostics;
    if(diagnostic){e.inspection_entered=true;e.validation_result="INCOMPLETE_SKIPPED";}
    if(e.fresh_count!=e.group_size)return;
    CandidateValidationCost validation_cost;
    try {
        if(diagnostic)e.validation_stage="ENTRY_CHECKPOINT";
        address_budget::checkpoint(diagnostic?"REWARD_VALIDATION_ENTRY":"REWARD_VALIDATION");
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
        if(diagnostic)e.validation_stage="FINAL_CHECKPOINT";
        address_budget::checkpoint("REWARD_VALIDATION_DONE");
        e.candidate=e.fresh_cost;e.candidate_valid=true;
        if(diagnostic){e.validation_stage="COMPLETE";e.validation_result="VALIDATED";}
    } catch(const address_budget::Deadline&){e.censored=true;if(diagnostic)e.validation_result="DEADLINE";}
      catch(const std::runtime_error&){e.invalid=true;if(diagnostic)e.validation_result="INVALID";}
}
inline bool admissible(){return pending().candidate_valid&&!pending().invalid&&!pending().censored;}

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
       <<",\"local_deadline\":"<<(address_budget::state().repair_deadline?"true":"false")
       <<",\"global_deadline\":"<<(address_budget::state().global_deadline?"true":"false")
       <<",\"deadline_stage\":\""<<(e.censored?address_budget::state().last_stage:"NONE")
       <<"\",\"deadline_resource\":\""<<(e.censored?address_budget::state().deadline_resource:"NONE")<<"\""
       <<",\"memory_eligible\":"<<(eligible?"true":"false")<<",\"bernoulli_reward\":"
       <<(eligible?(e.old_task>e.committed?"1":"0"):"null")
       <<",\"selection_wall_before_log_ns\":"<<address_budget::difference(end.wall,e.begin.wall)
       <<",\"selection_cpu_before_log_ns\":"<<address_budget::difference(end.cpu,e.begin.cpu);
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
    learn(e,alpha,beta);emit();
    if(invalid)throw std::runtime_error("reward: invalid joint candidate; rolled back");
}
inline void no_repair(const std::string& why,std::vector<int>& alpha,std::vector<int>& beta){
    auto& e=pending();
    if(e.old_group>=0)throw std::runtime_error("reward: no-repair after group deletion");
    e.stop=why;e.committed=e.old_task;
    e.censored=address_budget::state().global_deadline||address_budget::state().repair_deadline;
    e.outcome=e.censored?"CENSORED":"NO_GROUP";learn(e,alpha,beta);emit();
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
