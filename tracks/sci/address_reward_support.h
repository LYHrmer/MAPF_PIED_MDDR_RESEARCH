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
};
struct State {
    std::string mode="", trace;
    int width=0;
    long started=0, settled=0, errors=0;
    long long io_wall_ns=0, io_cpu_ns=0;
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
    s.event.begin=address_budget::tick();s.active=true;
}
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
    if(e.fresh_count!=e.group_size)return;
    try {
        address_budget::checkpoint("REWARD_VALIDATION");
        address_adapter::Paths paths;
        for(const auto& a:agents){
            paths.emplace_back();
            for(const auto& step:a.path){address_budget::checkpoint("REWARD_VALIDATION");paths.back().push_back(step.location);}
        }
        std::vector<bool> blocked(instance.map_size);
        for(int i=0;i<instance.map_size;++i){address_budget::checkpoint("REWARD_VALIDATION");blocked[i]=instance.isObstacle(i);}
        const int total=address_adapter::validate(paths,instance.num_of_rows,instance.num_of_cols,
            blocked,instance.getStarts(),instance.getGoals(),[](){address_budget::checkpoint("REWARD_VALIDATION");});
        if(static_cast<long long>(e.old_task)-e.old_group+e.fresh_cost!=total)
            throw std::runtime_error("reward: candidate SOC mismatch");
        address_budget::checkpoint("REWARD_VALIDATION_DONE");
        e.candidate=e.fresh_cost;e.candidate_valid=true;
    } catch(const address_budget::Deadline&){e.censored=true;}
      catch(const std::runtime_error&){e.invalid=true;}
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
       <<",\"selection_cpu_before_log_ns\":"<<address_budget::difference(end.cpu,e.begin.cpu)<<"}\n";
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
    out<<"]}";
}
} // namespace address_reward
