// Shared engineering only: cooperative wall/process-CPU deadline and cleanup reserve.
#pragma once
#include "address_adapter_support.h"
#include <ctime>
#include <exception>
#include <limits>
#include <memory>

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
struct State {
    ClockFunction wall = real_wall, cpu = real_cpu;
    bool configured=false, global_deadline=false, repair_deadline=false, search_active=false;
    bool preprocessing=false, preprocessing_fallback=false;
    double wall_stop=0, cpu_limit=0, cpu_reserve=0, local_stop=std::numeric_limits<double>::infinity();
    long group_calls=0,sipp_calls=0,sipp_deadlines=0,repair_deadlines=0,rollbacks=0;
    std::string last_stage="NONE", termination="NORMAL", last_sipp_end="NONE";
};
inline State& state() { static State s; return s; }
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
    const double wall=s.wall(),cpu=s.cpu();
    if(wall>=s.wall_stop||cpu>=s.cpu_limit-s.cpu_reserve) {
        s.global_deadline=true;s.termination="GLOBAL_DEADLINE";
    }
    if(s.global_deadline||wall>=s.local_stop||s.repair_deadline) {
        if(!s.repair_deadline && std::isfinite(s.local_stop))++s.repair_deadlines;
        s.repair_deadline=true;s.last_stage=stage;return true;
    }
    return false;
}
inline void checkpoint(const char* stage) { if(expired(stage))throw Deadline{}; }
inline void search_checkpoint(const char* stage) { if(state().search_active)checkpoint(stage); }
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
}
inline int finish() {
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
      <<",\"reward_semantics\":\"AUTHOR_ATTEMPT_UPDATE_BEFORE_ROLLBACK\",\"external_total_budget_verified\":false}\n";
    receipt.close();if(!receipt)throw std::runtime_error("budget: receipt write failed");
    return valid&&address_adapter::remaining()>=0&&s.cpu()<s.cpu_limit?0:74;
}
} // namespace address_budget
