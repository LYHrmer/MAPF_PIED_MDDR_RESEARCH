#define main preserved_legal_fixture_entry
#include "../legal_and_fixture.cpp"
#undef main
#include <fstream>
#include <map>
#include <set>
#include <sstream>
#include <chrono>

namespace {
void bound3(const R& x) {
    check(O::cmp(x,rat(0))>=0 && O::cmp(x,rat(32768))<0,"joint serialization range");
    long lo=0,hi=32768000000;
    while(hi-lo>1){const long m=lo+(hi-lo)/2;if(O::cmp(rat(m,1000000),x)<=0)lo=m;else hi=m;}
    std::cout<<"{\"lower\":"<<lo<<",\"upper\":"<<(same(x,rat(lo,1000000))?lo:hi)<<",\"denominator\":1000000}";
}
std::pair<long,long> direction(const std::string& h) {
    if(h=="EA")return {1,0};
    if(h=="WE")return {-1,0};
    if(h=="NO")return {0,-1};
    if(h=="SO")return {0,1};
    check(h=="W","invalid source direction");return {0,0};
}
struct Head5 { unsigned task,end;long gx,gy; };
struct Robot {
    unsigned agent,task,next=0;long x,y,gx,gy;bool ready=true,served=false;R released=rat(0);
    std::vector<Head5> heads;unsigned head_index=0,head_end=0;std::vector<std::string> route,deps;std::vector<std::pair<long,long>> public_path;std::shared_ptr<const R> wait_until;
};
struct History { std::string heading;R lower,upper;unsigned length;bool full_cap; };
// Every registered resource is an unchanged unit grid square.  The full unit
// cardinal sweep, footprint and error box lies inside this CLOSED AABB.  A
// strictly separated resource cannot enter any suffix mask.  Integer units
// of 1/20 preserve closed boundary contacts; Geometry remains the final test.
std::vector<G::Resource> coarse_cells(const std::vector<G::Resource>& input,
                                    long sx,long sy,long ex,long ey) {
    check(std::abs(ex-sx)+std::abs(ey-sy)<=1,"resource culling unit step support");
    const long xl=20*std::min(sx,ex)-3,xh=20*std::max(sx,ex)+3;
    const long yl=20*std::min(sy,ey)-3,yh=20*std::max(sy,ey)+3;
    std::vector<G::Resource> result;
    for(const auto& cell:input){
        check(cell.key.substr(0,5)=="cell-","resource culling grid key");
        const auto split=cell.key.find('-',5);check(split!=std::string::npos,"resource culling coordinate key");
        const long x=std::stol(cell.key.substr(5,split-5)),y=std::stol(cell.key.substr(split+1));
        if(20*x+10>=xl&&20*x-10<=xh&&20*y+10>=yl&&20*y-10<=yh)result.push_back(cell);
    }
    return result;
}
class EndOnlyActor {
    struct Count { unsigned success=0,total=0; };
    struct Agent { Count c;std::vector<unsigned> recent;std::vector<int> eta_history;std::shared_ptr<const R> delivered; };
    std::map<std::string,Count> counts;std::map<unsigned,Agent> agents;
    std::map<std::string,std::vector<R>> parameters;long rr_cursor=-1;
    mutable std::string macro_name;
    mutable unsigned initial_capacity=0;
    std::set<std::pair<unsigned,std::string>> skipped;
    std::map<unsigned,unsigned> public_head_parent;
    mutable unsigned pair_stage=0,anchor_agent=1000;
    mutable std::string anchor_move;
    mutable std::set<unsigned> anchor_tasks;
public:
    struct Claim { unsigned task,remaining,owners; };
    struct Candidate { std::string key,heading;unsigned agent;R launch;std::vector<Claim> claims;std::vector<R> features; };
    unsigned known=0,unknown=0;
    bool is_skipped(unsigned agent,const std::string& move)const{return skipped.count({agent,move})!=0;}
    void skip(unsigned agent,const std::string& move){check(skipped.insert({agent,move}).second,"duplicate occurrence skip");}
    bool accept_end(unsigned agent,const std::string& move){return skipped.erase({agent,move})!=0;}
    void skip_state()const{bool comma=false;for(const auto& x:skipped){if(comma)std::cout<<',';comma=true;std::cout<<"["<<x.first<<",\""<<x.second<<"\"]";}}

    void public_successor(unsigned previous,unsigned current){check(public_head_parent.emplace(current,previous).second,"duplicate public head identity");}
    bool is_public_successor(unsigned task)const{
        auto it=public_head_parent.find(task);
        while(it!=public_head_parent.end()){if(anchor_tasks.count(it->second))return true;it=public_head_parent.find(it->second);}
        return false;
    }
    void queried(unsigned agent){rr_cursor=static_cast<long>(agent);}
    void coefficient(const std::string& model,const R& x){parameters[model].push_back(x);}
    int decode(const History& h)const{
        if(!h.full_cap||h.length!=1||O::cmp(h.lower,h.upper)>0)return -1;
        const long lows[]={1083441,1292893,1732050},highs[]={1083442,1292894,1732051};bool supported=false;
        for(unsigned i=0;i<3;++i)if(O::cmp(h.lower,rat(lows[i],1000000))>=0&&O::cmp(h.upper,rat(highs[i],1000000))<=0)supported=true;
        if(!supported)return -1;
        return O::cmp(h.upper,rat(5,4))<0?1:O::cmp(h.lower,rat(5,4))>0?0:-1;
    }
    void receive(const History& h,unsigned id,const R& at){
        const int label=decode(h);if(label<0){++unknown;return;}
        auto& c=counts[h.heading];c.success+=static_cast<unsigned>(label);++c.total;
        auto& ag=agents[id];ag.c.success+=static_cast<unsigned>(label);++ag.c.total;
        int decoded_eta=-1;if(O::cmp(h.upper,rat(1083442,1000000))<=0)decoded_eta=1;else if(O::cmp(h.lower,rat(1292893,1000000))>=0&&O::cmp(h.upper,rat(1292894,1000000))<=0)decoded_eta=0;
        ag.eta_history.push_back(decoded_eta);if(ag.eta_history.size()>3)ag.eta_history.erase(ag.eta_history.begin());
        ag.recent.push_back(static_cast<unsigned>(label));if(ag.recent.size()>3)ag.recent.erase(ag.recent.begin());
        ag.delivered=std::make_shared<const R>(at);++known;
    }
    bool has_history(unsigned id)const{return agents.count(id)!=0;}
    R probability(unsigned id,bool recent)const{
        const auto it=agents.find(id);if(it==agents.end())return rat(1,2);
        if(!recent)return rat(it->second.c.success+1,it->second.c.total+2);
        unsigned sum=0;for(unsigned x:it->second.recent)sum+=x;return rat(sum+1,it->second.recent.size()+2);
    }
    R floor6(const R& x)const{
        check(O::cmp(x,rat(0))>=0&&O::cmp(x,rat(16))<=0,"public feature time range");long lo=0,hi=16000001;
        while(hi-lo>1){const long mid=lo+(hi-lo)/2;if(O::cmp(rat(mid,1000000),x)<=0)lo=mid;else hi=mid;}
        return rat(lo,1000000);
    }
    R survival_release_probability(unsigned agent,const R& age,bool history=true)const{
        const std::vector<int> empty;const auto& recent=history?agents.at(agent).eta_history:empty;unsigned plus=0,minus=0,zeros=0;
        for(int eta:recent){if(eta>0)++plus;else if(eta<0)++minus;else ++zeros;}
        std::vector<R> weights={rat(0),rat(0),rat(0)};
        if(zeros&&plus==0&&minus==0)weights[1]=rat(1);
        else if(!zeros){long lp=1,lm=1;for(unsigned i=0;i<plus;++i)lp*=9;for(unsigned i=0;i<minus;++i)lm*=9;
            const R posterior=rat(lp,lp+lm);weights[2]=O::add(rat(1,10),O::mul(rat(4,5),posterior));weights[0]=O::sub(rat(1),weights[2]);}
        else {weights[0]=rat(minus+1,recent.size()+3);weights[1]=rat(zeros+1,recent.size()+3);weights[2]=rat(plus+1,recent.size()+3);}
        R alive=rat(0),release=rat(0);
        for(unsigned j=0;j<3;++j){
            Controller hypothetical({rat(1),rat(2),rat(6),rat(1)},rat(1),rat(0),rat(1),rat(static_cast<long>(j)-1),"public-analytic-profile");
            check(hypothetical.run(rat(0)),"analytic profile RUN");hypothetical.advance_to(rat(4));const R total=hypothetical.snapshot().segment_start();
            // Normal END has not been delivered. Exclude hypotheses that would
            // already have produced END+1/4, including equality after dispatch.
            if(O::cmp(O::add(total,rat(1,4)),age)<=0)continue;
            alive=O::add(alive,weights[j]);
            Controller progress({rat(1),rat(2),rat(6),rat(1)},rat(1),rat(0),rat(1),rat(static_cast<long>(j)-1),"public-analytic-profile");
            check(progress.run(rat(0)),"analytic progress RUN");progress.advance_to(age);
            if(O::cmp(progress.snapshot().state().s,rat(13,20))>0)release=O::add(release,weights[j]);
        }
        return O::cmp(alive,rat(0))>0?O::div(release,alive):rat(0);
    }
    void features(Candidate& c,const std::vector<R>& structural,const R& at)const{
        const R age=O::sub(at,c.launch);const R prior=survival_release_probability(c.agent,age,false),conditional=survival_release_probability(c.agent,age,true);
        c.features={prior};c.features.insert(c.features.end(),structural.begin(),structural.end());
        const auto& ag=agents.at(c.agent);const auto it=counts.find(c.heading);const Count hc=it==counts.end()?Count{}:it->second;
        const R rp=probability(c.agent,true);
        const R elapsed=O::sub(at,*ag.delivered);const R recency=O::cmp(elapsed,rat(16))<0?O::div(floor6(elapsed),rat(16)):rat(1);
        const std::vector<R> history={conditional,rp,rat(ag.recent.back()),rat(hc.success+1,hc.total+2),rat(std::min(ag.c.total,8U),8),recency,O::mul(conditional,structural.at(2)),O::mul(conditional,structural.at(1))};
        c.features.insert(c.features.end(),history.begin(),history.end());
        check(O::cmp(age,rat(16))<=0,"candidate source age support");c.features.push_back(O::div(floor6(age),rat(2)));c.features.push_back(O::mul(prior,structural.at(2)));
    }
    std::string choose(const std::vector<Candidate>& input,const R& at,unsigned capacity,const std::string& policy,unsigned opportunity,const std::string& trigger)const{
        const std::vector<std::string> options={"C","LD"};
        if(initial_capacity==0){check(capacity==8||capacity==16,"R13 initial public budget");initial_capacity=capacity;}
        std::vector<Candidate> visible=input;
        for(auto& c:visible){
            const R budget=rat(capacity,16),time=O::div(floor6(O::div(at,rat(8))),rat(16));
            c.features.push_back(budget);c.features.push_back(time);
            c.features.push_back(O::mul(budget,c.features.at(19)));c.features.push_back(O::mul(budget,O::sub(rat(1),time)));
            check(c.features.size()==24,"R13 original candidate feature dimensions");
        }
        auto top_candidate=[&](bool distinct)->const Candidate*{
            const Candidate* target=nullptr;R best=rat(0);
            for(const auto& c:visible){
                if(distinct&&c.agent==anchor_agent&&c.key==anchor_move)continue;
                R score=rat(0);const R probability=survival_release_probability(c.agent,O::sub(at,c.launch));
                for(const auto& claim:c.claims)score=O::add(score,O::div(probability,rat(claim.remaining*claim.owners)));
                if(!target||O::cmp(score,best)>0||(same(score,best)&&(c.agent<target->agent||(c.agent==target->agent&&c.key<target->key)))){target=&c;best=score;}
            }
            return target;
        };
        if(policy=="WAIT")macro_name="W";
        if(macro_name.empty()&&capacity>0&&initial_capacity-capacity>=initial_capacity/2){
            const auto inference_start=std::chrono::steady_clock::now();
            const Candidate* target=top_candidate(false);check(target!=nullptr,"R13 late gate lacks target");
            R inverse=rat(0);unsigned minimum=target->claims.front().remaining;
            for(const auto& claim:target->claims){inverse=O::add(inverse,rat(1,claim.remaining*claim.owners));minimum=std::min(minimum,claim.remaining);}
            const R probability=target->features.at(10);
            const std::vector<R> gate={probability,target->features.at(0),target->features.at(18),inverse,rat(minimum,64),rat(target->claims.size(),15),rat(visible.size()-1,15),rat(capacity,16),O::sub(rat(1),target->features.at(21)),O::mul(probability,inverse)};
            std::vector<R> task_scores(2,rat(0)),time_scores(2,rat(0)),scores(2,rat(0));
            R margin=rat(0);bool infinite=false,learned=false;unsigned selected_option=0;
            if(policy=="alwaysLD"||policy=="macro_LD")selected_option=1;
            else if(policy=="budget_lookup"){
                const auto& value=parameters.at("budget_lookup_"+std::to_string(initial_capacity));check(value.size()==1,"budget lookup binding");
                check(same(value[0],rat(0))||same(value[0],rat(1)),"budget lookup option range");selected_option=same(value[0],rat(1))?1:0;
            } else if(policy=="full"||policy=="no_history_prob"){
                learned=true;const auto& threshold=parameters.at("shared_margin");check(threshold.size()==2,"shared CAL threshold binding");infinite=same(threshold[0],rat(1));margin=threshold[1];
                for(unsigned head=0;head<2;++head){
                    const auto& coefficient=parameters.at(policy+"_LD"+(head==0?"_tasks":"_time"));check(coefficient.size()==11,"R13 ridge coefficient dimensions");R value=coefficient[0];
                    for(unsigned j=0;j<10;++j)if(!(policy=="no_history_prob"&&(j==0||j==9)))value=O::add(value,O::mul(coefficient[j+1],gate[j]));
                    if(head==0)task_scores[1]=value;else time_scores[1]=value;
                }
                scores[1]=O::add(task_scores[1],time_scores[1]);if(!infinite&&O::cmp(scores[1],margin)>0)selected_option=1;
            } else check(policy=="condition"||policy=="macro_C","R13 gate policy support");
            macro_name=options[selected_option];
            const auto inference_ns=learned?std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now()-inference_start).count():0;
            std::cout<<"{\"event\":\"macro_choice\",\"at\":";bound3(at);
            std::cout<<",\"policy\":\""<<policy<<"\",\"opportunity\":"<<opportunity<<",\"initial_capacity\":"<<initial_capacity<<",\"remaining_capacity\":"<<capacity<<",\"spent\":"<<(initial_capacity-capacity)<<",\"target_agent\":"<<target->agent<<",\"target_move\":\""<<target->key<<"\",\"feature_schema\":\"late_target10_v1\",\"features\":[";
            bool comma=false;for(const auto& x:gate){if(comma)std::cout<<',';comma=true;std::cout<<'"'<<exact(x)<<'"';}
            std::cout<<"],\"learned\":"<<(learned?"true":"false")<<",\"margin_infinite\":"<<(infinite?"true":"false")<<",\"margin\":\""<<exact(margin)<<"\",\"scores\":[";
            for(unsigned k=0;k<2;++k){if(k)std::cout<<',';std::cout<<"{\"option\":\""<<options[k]<<"\",\"tasks\":\""<<exact(task_scores[k])<<"\",\"time\":\""<<exact(time_scores[k])<<"\",\"total\":\""<<exact(scores[k])<<"\"}";}
            std::cout<<"],\"selected_option\":\""<<macro_name<<"\",\"inference_calls\":"<<(learned?1:0)<<",\"inference_ns\":"<<inference_ns<<"}\n";
        }
        std::string scoring_policy=macro_name=="W"?"WAIT":"condition";unsigned intervention_index=0;std::vector<std::string> second_eligible;
        const bool first=macro_name=="LD"&&pair_stage==0&&capacity>0,second=macro_name=="LD"&&pair_stage==1&&capacity>0;
        if(first||second){
            if(second)for(const auto& c:visible)if(!(c.agent==anchor_agent&&c.key==anchor_move))second_eligible.push_back(c.key);
            const Candidate* target=top_candidate(second);
            if(target){
                scoring_policy="force_SKIP"+std::to_string(target->agent);intervention_index=first?1:2;pair_stage=intervention_index;
                if(first){anchor_agent=target->agent;anchor_move=target->key;for(const auto& c:target->claims)anchor_tasks.insert(c.task);}
            }
        }
        std::string selected,selected_kind="WAIT";R best=rat(0);unsigned best_agent=1000,best_kind=2;
        std::cout<<"{\"event\":\"actor_decision\",\"at\":";bound3(at);
        std::cout<<",\"policy\":\""<<policy<<"\",\"remaining_capacity\":"<<capacity<<",\"decision_mode\":\""<<scoring_policy<<"\",\"opportunity\":"<<opportunity<<",\"trigger\":\""<<trigger<<"\",\"RR_cursor\":"<<rr_cursor<<",\"candidates\":[";
        bool comma=false;
        for(const auto& c:visible){
            check(O::cmp(O::sub(at,c.launch),rat(3,4))>=0,"R13 original age gate");check(has_history(c.agent)&&known>=2,"R13 original public history gate");
            const R p=survival_release_probability(c.agent,O::sub(at,c.launch));std::vector<R> scores={rat(0),rat(0)};
            for(unsigned kind=0;kind<2;++kind){
                R score=rat(0);const std::string name=kind==0?"QUERY":"SKIP";
                if(scoring_policy.substr(0,6)=="force_")score=scoring_policy.substr(6)==name+std::to_string(c.agent)?rat(1):rat(0);
                else if(scoring_policy=="condition"&&kind==0)for(const auto& cl:c.claims)score=O::add(score,O::div(p,rat(cl.remaining*cl.owners)));
                scores[kind]=score;const bool tie=kind<best_kind||(kind==best_kind&&(c.agent<best_agent||(c.agent==best_agent&&c.key<selected)));
                if(capacity&&O::cmp(score,rat(0))>0&&(selected.empty()||O::cmp(score,best)>0||(same(score,best)&&tie))){selected=c.key;selected_kind=name;best=score;best_agent=c.agent;best_kind=kind;}
            }
            if(comma)std::cout<<',';
            comma=true;
            std::cout<<"{\"move\":\""<<c.key<<"\",\"agent\":"<<c.agent<<",\"heading\":\""<<c.heading<<"\",\"public_launch\":";bound3(c.launch);
            std::cout<<",\"probability\":\""<<exact(p)<<"\",\"score\":\""<<exact(scores[0])<<"\",\"skip_score\":\""<<exact(scores[1])<<"\",\"claims\":[";
            bool cc=false;for(const auto& cl:c.claims){if(cc)std::cout<<',';cc=true;std::cout<<"{\"task\":"<<cl.task<<",\"remaining_route_items\":"<<cl.remaining<<",\"owners\":"<<cl.owners<<'}';}
            std::cout<<"],\"features\":[";bool ff=false;for(const auto& z:c.features){if(ff)std::cout<<',';ff=true;std::cout<<'"'<<exact(z)<<'"';}std::cout<<"]}";
        }
        std::cout<<"],\"macro\":\""<<macro_name<<"\",\"initial_capacity\":"<<initial_capacity<<",\"intervention_index\":"<<intervention_index<<",\"pair_stage\":"<<pair_stage<<",\"anchor_agent\":"<<anchor_agent<<",\"anchor_move\":\""<<anchor_move<<"\",\"anchor_tasks\":[";
        bool ac=false;for(unsigned task:anchor_tasks){if(ac)std::cout<<',';ac=true;std::cout<<task;}
        std::cout<<"],\"second_eligible\":[";ac=false;for(const auto& key:second_eligible){if(ac)std::cout<<',';ac=true;std::cout<<'"'<<key<<'"';}
        std::cout<<"],\"head_lineage_count\":"<<public_head_parent.size()<<",\"selected\":\""<<selected<<"\",\"selected_kind\":\""<<selected_kind<<"\",\"END_only_known\":"<<known<<",\"END_unknown\":"<<unknown<<",\"private_progress_input\":false,\"regime_input\":false,\"future_head_input\":false}\n";
        return selected_kind=="SKIP"?"SKIP:"+selected:selected;
    }
};
struct Move3 {
    std::string key,heading;unsigned robot,leg;long sx,sy,ex,ey;G geometry;R launch;
    Controller controller;bool physical=false,native=false;std::shared_ptr<const R> ended,delivery;
    Move3(const std::string& k,const std::string& h,unsigned rr,unsigned ll,const G& g,long x,long y,long xx,long yy,
          const R& at,const R& eta)
        :key(k),heading(h),robot(rr),leg(ll),sx(x),sy(y),ex(xx),ey(yy),geometry(g),launch(at),
         controller({rat(1),rat(2),rat(6),rat(1)},rat(1),at,rat(1),eta,k) {
        check(controller.run(at),"joint original MOVE RUN failed");
    }
};
class World3 {
    std::vector<Robot> robots;std::vector<G::Resource> cells;
    std::map<std::pair<unsigned,unsigned>,long> private_eta;std::vector<std::unique_ptr<Move3>> moves;
    std::unique_ptr<P> owner;EndOnlyActor actor;std::map<std::string,std::unique_ptr<G>> wanted_geometry;
    std::map<std::string,unsigned> requester_robot;std::set<std::string> asked;std::set<std::string> opportunity_consumed;
    R clock=rat(0),horizon=rat(128);unsigned rows=0,cols=0,plan_round=0,revision=0,capacity;
    std::map<std::pair<long,long>,std::string> last_depart;std::set<std::string> launched;std::string policy;unsigned eligible_opportunities=0;
    unsigned target_tasks=0,served=0,started=0,feedback=0,max_candidates=0;R completion_sum=rat(0),flow_sum=rat(0);
    std::string cell_name(long x,long y)const{return "cell-"+std::to_string(x)+"-"+std::to_string(y);}
    std::string key(unsigned n,unsigned leg)const{return "m-"+std::to_string(robots[n].agent)+"-"+std::to_string(leg);}
    S::Delta delta(const std::string& tag)const {
        return {{owner->view().structure().view_id,tag+"-"+std::to_string(revision+1),{},{},{}},clock,{},{}};
    }
    void commit(S::Delta& d,const pie_query::Map<P::SnapshotIds>& ids={}) {
        auto next=owner->prepare_admitted_update(d,ids);owner->commit(std::move(next));++revision;
    }
    G geometry(unsigned n,unsigned leg)const {
        const auto& r=robots[n];const auto dv=direction(r.route.at(leg));
        return G({{"PIED74cfba3-joint-R3","exact-flint","column-row-plane","grid-unit",key(n,leg)},
            {rat(r.x),rat(r.y)},{rat(r.x+dv.first),rat(r.y+dv.second)},
            {square(rat(0),rat(0),rat(1,10))},{{rat(-1,20),rat(-1,20)},{rat(1,20),rat(1,20)}},
            coarse_cells(cells,r.x,r.y,r.x+dv.first,r.y+dv.second)},true);
    }
    std::shared_ptr<const I::Action> action3(unsigned n,const G& g)const {
        return std::make_shared<const I::Action>(I::Action{"agent-"+std::to_string(robots[n].agent),
            "joint-native-certified-not-AUTH","fixed-reference-unit-profile",g,rat(0),rat(1),std::make_shared<const R>(rat(1,10)),true});
    }
    Move3* active(unsigned n)const{for(const auto& m:moves)if(m->robot==n&&!m->native)return m.get();return nullptr;}
    void event(const char* what,const std::string& id)const {
        std::cout<<"{\"event\":\""<<what<<"\",\"id\":\""<<id<<"\",\"at\":";bound3(clock);std::cout<<"}\n";
    }
    bool precedence(unsigned n)const {
        const auto& r=robots[n];return r.next>=r.deps.size()||r.deps[r.next].empty()||launched.count(r.deps[r.next]);
    }
    void replenish() {
        for(unsigned batch=0;batch<4;++batch){
            unsigned backlog=0;for(unsigned n=0;n<robots.size();++n)backlog=std::max(backlog,static_cast<unsigned>(robots[n].route.size()-robots[n].next)+(active(n)?1U:0U));
            if(backlog>=4)return;
            std::cout<<"{\"event\":\"planner_request\",\"round\":"<<plan_round++<<",\"at\":";bound3(clock);
            std::cout<<",\"rows\":"<<rows<<",\"cols\":"<<cols<<",\"starts\":[";
            for(unsigned n=0;n<robots.size();++n){if(n)std::cout<<',';const auto& p=robots[n].public_path.back();std::cout<<p.second*cols+p.first;}
            std::cout<<"],\"goals\":[";
            for(unsigned n=0;n<robots.size();++n){if(n)std::cout<<',';const auto& r=robots[n];std::cout<<"{\"location\":"<<r.gy*cols+r.gx<<",\"id\":"<<r.task<<'}';}
            std::cout<<"],\"frontier_is_committed_plan_not_private_progress\":true}\n"<<std::flush;
            std::vector<int> actions(robots.size());for(auto& a:actions){check(bool(std::cin>>a),"official planner reply missing");check(a>=0&&a<5,"official action outside support");}
            const std::string headings[]={"EA","SO","WE","NO","W"};std::vector<std::pair<long,long>> ends;std::set<std::pair<long,long>> unique;
            for(unsigned n=0;n<robots.size();++n){const auto at=robots[n].public_path.back(),dv=direction(headings[actions[n]]);const auto end=std::make_pair(at.first+dv.first,at.second+dv.second);check(unique.insert(end).second,"official vertex conflict");ends.push_back(end);
                for(unsigned b=0;b<n;++b)check(!(at==ends[b]&&end==robots[b].public_path.back()&&at!=end),"official edge swap");
                if(actions[n]!=4)last_depart[at]=key(n,robots[n].route.size());}
            for(unsigned n=0;n<robots.size();++n){auto& r=robots[n];if(actions[n]==4)continue;
                auto dep=last_depart.find(ends[n]);r.deps.push_back(dep==last_depart.end()?"":dep->second);r.route.push_back(headings[actions[n]]);r.public_path.push_back(ends[n]);r.head_end=r.route.size();
                std::cout<<"{\"event\":\"official_move_committed\",\"round\":"<<plan_round-1<<",\"agent\":"<<r.agent<<",\"move\":\""<<key(n,r.route.size()-1)<<"\",\"dependency_departure_started\":\""<<r.deps.back()<<"\",\"start\":["<<r.public_path[r.public_path.size()-2].first<<','<<r.public_path[r.public_path.size()-2].second<<"],\"end\":["<<ends[n].first<<','<<ends[n].second<<"],\"at\":";bound3(clock);std::cout<<"}\n";
            }
        }
    }
    void rebuild_demands() {
        auto d=delta("demands");
        for(const auto& old:owner->view().structure().demands)d.structure.demands.emplace(old.first,nullptr);
        wanted_geometry.clear();requester_robot.clear();
        for(unsigned n=0;n<robots.size();++n){const auto& r=robots[n];
            if(!r.ready || r.next>=r.route.size() || !precedence(n))continue;
            const std::string id="d-"+std::to_string(r.agent)+"-"+std::to_string(r.next);
            std::unique_ptr<G> g(new G(geometry(n,r.next)));const auto full=g->n_mask(rat(0),rat(1));
            const auto old=owner->view().structure().demands.find(id);
            const R joined=old==owner->view().structure().demands.end()?clock:old->second->input->joined;
            d.structure.demands[id]=std::make_shared<const I::Demand>(I::Demand{
                "agent-"+std::to_string(r.agent),"",full.mask(),joined,true});
            wanted_geometry.emplace(id,std::move(g));requester_robot.emplace(id,n);
        }
        commit(d);
    }
    void start_ready() {
        bool changed=true;
        while(changed){changed=false;
            for(unsigned n=0;n<robots.size();++n){auto& r=robots[n];
                if(!r.ready || r.next>=r.route.size() || !precedence(n))continue;
                if(r.route[r.next]=="W") {
                    r.ready=false;r.wait_until=std::make_shared<const R>(O::add(clock,rat(1)));++r.next;
                    event("public_WAIT_started",std::to_string(r.agent));changed=true;continue;
                }
                const std::string demand="d-"+std::to_string(r.agent)+"-"+std::to_string(r.next);
                if(!owner->view().structure().demands.count(demand) || !ready(owner->view(),demand))continue;
                const auto& g=*wanted_geometry.at(demand);auto d=delta("RUN");const auto full=g.n_mask(rat(0),rat(1));
                const std::string id=key(n,r.next),agent="agent-"+std::to_string(r.agent);
                d.structure.actions.emplace(id,action3(n,g));
                for(const auto& c:full.mask()) {
                    const auto old=owner->view().structure().owners.find(c);
                    check(old==owner->view().structure().owners.end() || old->second.agent==agent,"joint grant conflicts with foreign physical owner");
                    d.structure.owners.emplace(c,std::make_shared<const I::Owner>(I::Owner{id,agent,id,true}));
                }
                d.structure.demands.emplace(demand,nullptr);commit(d,{{id,{id+"-seed",id+"-current","",""}}});
                const unsigned leg=r.next++;const auto dv=direction(r.route[leg]);
                const long eta=private_eta.at({r.agent,leg});
                moves.emplace_back(new Move3(id,r.route[leg],n,leg,g,r.x,r.y,r.x+dv.first,r.y+dv.second,clock,rat(eta)));
                r.ready=false;++started;launched.insert(id);event("original_RUN",id);changed=true;
            }
            if(changed)rebuild_demands();
        }
    }
    void advance_physics(const R& at) {
        clock=at;
        for(auto& m:moves){if(m->physical)continue;m->controller.advance_to(at);const auto s=m->controller.snapshot();
            if(!s.closed())continue;
            check(same(s.state().s,rat(1)) && same(s.state().v,rat(0)),"joint physical original END not at rest/endpoint");
            m->physical=true;m->ended=std::make_shared<const R>(at);m->delivery=std::make_shared<const R>(O::add(at,rat(1,4)));
            robots[m->robot].x=m->ex;robots[m->robot].y=m->ey;event("physical_original_END",m->key);
        }
    }
    void service_heads() {
        for(unsigned n=0;n<robots.size();++n){auto& r=robots[n];if(r.served || r.x!=r.gx || r.y!=r.gy)continue;
            const auto* m=active(n);if(m && (!m->physical || !same(m->controller.snapshot().state().v,rat(0))))continue;

            r.served=true;++served;completion_sum=O::add(completion_sum,clock);flow_sum=O::add(flow_sum,O::sub(clock,r.released));
            std::cout<<"{\"event\":\"task_service\",\"agent\":"<<r.agent<<",\"task\":"<<r.task<<",\"goal\":["<<r.gx<<','<<r.gy
                     <<"],\"at\":";bound3(clock);std::cout<<",\"original_endpoint_at_rest\":true,\"physical_footprint_inside_service_square\":true}\n";
        }
    }
    void deliver() {
        for(auto& m:moves){if(!m->physical || m->native || !same(*m->delivery,clock))continue;
            const auto before=owner->view();const auto endpoint=m->geometry.n_mask(rat(1),rat(1)).mask();auto d=delta("normal-END");
            d.structure.actions.emplace(m->key,nullptr);
            for(const auto& o:before.structure().owners)if(o.second.action==m->key){
                const bool keep=std::find(endpoint.begin(),endpoint.end(),o.first)!=endpoint.end();
                d.structure.owners.emplace(o.first,keep?std::make_shared<const I::Owner>(I::Owner{
                    "resident-"+std::to_string(robots[m->robot].agent),"agent-"+std::to_string(robots[m->robot].agent),"",false}):nullptr);
            }
            commit(d);m->native=true;robots[m->robot].ready=true;
            const R duration=O::sub(*m->ended,m->launch);
            // The actor receives only delivered END duration; never motor progress or eta.
            History h{m->heading,duration,duration,1,true};const int recovered=actor.decode(h);actor.receive(h,robots[m->robot].agent,clock);++feedback;
            std::cout<<"{\"event\":\"public_END_delivered\",\"move\":\""<<m->key<<"\",\"agent\":"<<robots[m->robot].agent
                     <<",\"heading\":\""<<m->heading<<"\",\"at\":";bound3(clock);
            std::cout<<",\"public_original_END\":";bound3(*m->ended);std::cout<<",\"public_launch\":";bound3(m->launch);
            std::cout<<",\"duration\":";bound3(duration);std::cout<<",\"decoded_END_class\":"<<recovered
                     <<",\"full_cap_uninterrupted\":true,\"length\":1,\"progress_field_sent_to_actor\":false}\n";
            if(actor.accept_end(robots[m->robot].agent,m->key))event("public_SKIP_cleared_normal_END",m->key);
            event("native_READY",m->key);
            auto& r=robots[m->robot];if(r.served && r.head_index+1<r.heads.size()){
                const unsigned previous_public_task=r.task;
                ++r.head_index;const auto& head=r.heads[r.head_index];r.task=head.task;r.gx=head.gx;r.gy=head.gy;r.served=false;r.released=clock;++target_tasks;
                std::cout<<"{\"event\":\"public_head_revealed\",\"agent\":"<<r.agent<<",\"head_index\":"<<r.head_index<<",\"task\":"<<r.task<<",\"head_end\":"<<r.head_end<<",\"goal\":["<<r.gx<<','<<r.gy<<"],\"at\":";bound3(clock);std::cout<<",\"previous_service_and_END\":true}\n";
                actor.public_successor(previous_public_task,r.task);
            }
        }
        for(auto& r:robots)if(r.wait_until && same(*r.wait_until,clock)){r.wait_until.reset();r.ready=true;event("public_WAIT_ended",std::to_string(r.agent));}
        replenish();rebuild_demands();start_ready();
    }
    std::vector<EndOnlyActor::Candidate> candidates()const {
        std::vector<EndOnlyActor::Candidate> out;
        for(const auto& m:moves){if(m->native || asked.count(m->key) || O::cmp(O::sub(clock,m->launch),rat(3,4))<0 || !actor.has_history(robots[m->robot].agent) || actor.known<2)continue;
            EndOnlyActor::Candidate c{m->key,m->heading,robots[m->robot].agent,m->launch,{},{}};
            for(const auto& d:owner->view().structure().demands){
                const auto it=requester_robot.find(d.first);check(it!=requester_robot.end(),"public requester index missing");
                const auto& r=robots[it->second];
                for(const auto& rel:d.second->relations)if(rel.action==m->key && rel.retirable && rel.threshold)
                    c.claims.push_back({r.task,static_cast<unsigned>(r.head_end-r.next),static_cast<unsigned>(d.second->relations.size())});
            }
            if(!c.claims.empty()){
                unsigned claims=0,remaining=0,owners=0,intersections=0,intrusions=0,index_sum=0,intruder_remaining=0,goal_blocks=0;R inverse=rat(0);
                for(const auto& d:owner->view().structure().demands){
                    bool relevant=false;for(const auto& rel:d.second->relations)if(rel.action==m->key&&rel.retirable&&rel.threshold)relevant=true;
                    if(!relevant)continue;
                    const unsigned rr=requester_robot.at(d.first);const auto& request=robots[rr];++claims;
                    const unsigned begin=request.next;remaining+=static_cast<unsigned>(request.head_end)-begin;owners+=static_cast<unsigned>(d.second->relations.size());
                    inverse=O::add(inverse,rat(1,request.head_end-begin));
                    std::set<std::pair<long,long>> path(request.public_path.begin()+begin,request.public_path.begin()+request.head_end+1);
                    for(unsigned n=0;n<robots.size();++n){if(n==rr)continue;const auto& other=robots[n];const auto* am=active(n);
                        const unsigned ob=am?am->leg:other.next;
                        std::set<std::pair<long,long>> op(other.public_path.begin()+ob,other.public_path.begin()+other.head_end+1);
                        for(const auto& point:path)if(op.count(point))++intersections;
                        const auto end=std::make_pair(other.gx,other.gy);
                        if(path.count(end)){++intrusions;intruder_remaining+=static_cast<unsigned>(other.head_end)-ob;
                            for(unsigned j=begin;j<=request.head_end;++j)if(request.public_path[j]==end){index_sum+=j-begin;break;}}
                        if(op.count(std::make_pair(request.gx,request.gy)))++goal_blocks;
                    }
                }
                actor.features(c,{rat(claims,robots.size()-1),rat(remaining,64),inverse,rat(owners,robots.size()-1),rat(intersections,256),rat(intrusions,robots.size()-1),rat(index_sum,64),rat(intruder_remaining,64),rat(goal_blocks,robots.size()-1)},clock);
                out.push_back(c);
            }
        }
        return out;
    }
    void queries(const std::string& trigger) {
        for(const auto& m:moves)if(!opportunity_consumed.count(m->key)&&same(O::add(m->launch,rat(3,4)),clock))opportunity_consumed.insert(m->key);
        const auto raw_input=candidates();std::vector<EndOnlyActor::Candidate> input;
        std::cout<<"{\"event\":\"public_candidate_visibility\",\"at\":";bound3(clock);
        std::cout<<",\"skip_state\":[";actor.skip_state();std::cout<<"],\"raw_candidates\":[";bool rc=false;
        for(const auto& c:raw_input){if(rc)std::cout<<',';rc=true;std::cout<<"["<<c.agent<<",\""<<c.key<<"\"]";if(!actor.is_skipped(c.agent,c.key))input.push_back(c);}
        std::cout<<"],\"visible_candidates\":[";rc=false;for(const auto& c:input){if(rc)std::cout<<',';rc=true;std::cout<<"["<<c.agent<<",\""<<c.key<<"\"]";}std::cout<<"]}\n";
        std::cout<<"{\"event\":\"opportunity_census\",\"at\":";bound3(clock);std::cout<<",\"candidates\":"<<input.size()<<",\"trigger\":\""<<trigger<<"\"}\n";if(input.empty())return;
        ++eligible_opportunities;max_candidates=std::max(max_candidates,static_cast<unsigned>(input.size()));
        check(asked.size()<=capacity,"joint actor capacity exceeded");
        const std::string selected=actor.choose(input,clock,capacity-static_cast<unsigned>(asked.size()),policy,eligible_opportunities,trigger);
        if(selected.empty())return;
        if(selected.substr(0,5)=="SKIP:"){
            const std::string key=selected.substr(5);const auto c=std::find_if(input.begin(),input.end(),[&](const EndOnlyActor::Candidate& x){return x.key==key;});
            check(c!=input.end(),"skip selected unknown public occurrence");actor.skip(c->agent,c->key);event("public_SKIP_installed",c->key);return;
        }
        Move3* chosen=nullptr;for(auto& m:moves)if(m->key==selected)chosen=m.get();check(chosen!=nullptr,"actor selected unknown source");
        const auto before=owner->view();query(*owner,chosen->controller,clock,"joint-POSITION-"+selected);asked.insert(selected);if(policy=="RR")actor.queried(robots[chosen->robot].agent);++revision;
        std::cout<<"{\"event\":\"certified_POSITION_committed\",\"move\":\""<<selected<<"\",\"at\":";bound3(clock);
        std::cout<<",\"certified_lower\":";bound3(owner->view().structure().actions.at(selected)->input->q);
        std::cout<<",\"epsilon\":\"1/10\",\"removed\":[";bool comma=false;
        for(const auto& o:before.structure().owners)if(o.second.action==selected&&!owner->view().structure().owners.count(o.first)){if(comma)std::cout<<',';comma=true;std::cout<<'"'<<o.first<<'"';}
        std::cout<<"],\"endpoint_retained\":true}\n";rebuild_demands();start_ready();
    }
    void frame()const {
        std::cout<<"{\"event\":\"world_frame_offline_only\",\"at\":";bound3(clock);std::cout<<",\"owners\":[";
        bool comma=false;for(const auto& o:owner->view().structure().owners){if(comma)std::cout<<',';
            comma=true;
            std::cout<<"[\""<<o.first<<"\",\""<<o.second.agent<<"\",\""<<o.second.action<<"\"]";}
        std::cout<<"],\"actions\":[";comma=false;
        for(const auto& a:owner->view().structure().actions){if(comma)std::cout<<',';
            comma=true;
            std::cout<<"{\"id\":\""<<a.first<<"\",\"q\":";bound3(a.second->input->q);std::cout<<",\"mask\":[";
            bool mc=false;for(const auto& c:owner->view().current_snapshot(a.first).mask()){if(mc)std::cout<<',';mc=true;std::cout<<'"'<<c<<'"';}std::cout<<"]}";}
        std::cout<<"],\"demands\":[";comma=false;
        for(const auto& d:owner->view().structure().demands){if(comma)std::cout<<',';
            comma=true;
            std::cout<<"{\"id\":\""<<d.first<<"\",\"agent\":\""<<d.second->input->agent<<"\",\"resources\":[";
            bool rc=false;for(const auto& c:d.second->input->resources){if(rc)std::cout<<',';rc=true;std::cout<<'"'<<c<<'"';}
            std::cout<<"],\"relations\":[";rc=false;for(const auto& rel:d.second->relations){if(rc)std::cout<<',';rc=true;
                std::cout<<"{\"action\":\""<<rel.action<<"\",\"threshold\":";
                if(rel.threshold)std::cout<<'"'<<exact(*rel.threshold)<<'"';else std::cout<<"null";
                std::cout<<",\"retirable\":"<<(rel.retirable?"true":"false")<<'}';}
            std::cout<<"]}";
        }
        std::cout<<"],\"robots\":[";comma=false;std::set<std::string> actual_resources;
        for(unsigned n=0;n<robots.size();++n){const auto& r=robots[n];const auto* m=active(n);R s=rat(0),v=rat(0),x=rat(r.x),y=rat(r.y);
            std::vector<std::string> footprint;
            if(m){s=m->controller.snapshot().state().s;v=m->controller.snapshot().state().v;
                x=O::add(rat(m->sx),O::mul(s,rat(m->ex-m->sx)));y=O::add(rat(m->sy),O::mul(s,rat(m->ey-m->sy)));
                footprint=m->geometry.n_mask(s,s).mask();}
            else footprint={cell_name(r.x,r.y)};
            for(const auto& c:footprint){check(actual_resources.insert(c).second,"joint actual enlarged footprints share a resource");
                const auto own=owner->view().structure().owners.find(c);
                check(own!=owner->view().structure().owners.end() && own->second.agent=="agent-"+std::to_string(r.agent),"joint actual footprint lacks exclusive physical owner");}
            if(comma)std::cout<<',';
            comma=true;
            std::cout<<"{\"agent\":"<<r.agent<<",\"task\":"<<r.task<<",\"next\":"<<r.next<<",\"head_index\":"<<r.head_index<<",\"head_end\":"<<r.head_end<<",\"served\":"<<(r.served?"true":"false")
                     <<",\"ready\":"<<(r.ready?"true":"false")<<",\"active\":\""<<(m?m->key:"")<<"\",\"x\":";bound3(x);
            std::cout<<",\"y\":";bound3(y);std::cout<<",\"s\":";bound3(s);std::cout<<",\"v\":";bound3(v);
            std::cout<<",\"actual_enlarged_mask\":[";bool fc=false;for(const auto& c:footprint){if(fc)std::cout<<',';fc=true;std::cout<<'"'<<c<<'"';}std::cout<<"]}";
        }
        std::cout<<"],\"actor_consumes_this_frame\":false}\n";
    }
public:
    World3(const char* input,const std::string& pp,unsigned b):capacity(b),policy(pp) {
        std::ifstream f(input);check(bool(f),"joint input missing");std::string kind;
        while(f>>kind){if(kind=="C"){long x,y;f>>x>>y;cells.push_back({cell_name(x,y),{square(rat(x),rat(y),rat(1,2))}});}
            else if(kind=="D"){long h;f>>rows>>cols>>h;horizon=rat(h);}
            else if(kind=="R"){Robot r;f>>r.agent>>r.task>>r.x>>r.y>>r.gx>>r.gy;r.public_path.push_back({r.x,r.y});r.heads.push_back({r.task,0,r.gx,r.gy});robots.push_back(std::move(r));}
            else if(kind=="F"){unsigned agent,task;long gx,gy;f>>agent>>task>>gx>>gy;Robot* target=nullptr;for(auto& r:robots)if(r.agent==agent)target=&r;check(target!=nullptr,"future FIFO robot missing");target->heads.push_back({task,0,gx,gy});}
            else if(kind=="M"){std::string model;long num;unsigned long den;f>>model>>num>>den;actor.coefficient(model,rat(num,den));}
            else if(kind=="E"){unsigned agent,leg;long eta;f>>agent>>leg>>eta;check(eta>=-1&&eta<=1,"private eta outside promise");private_eta.emplace(std::make_pair(agent,leg),eta);}
            else throw std::runtime_error("unknown joint input record");
            check(bool(f),"malformed joint input");}
        check((robots.size()>=2&&robots.size()<=16) && cells.size()>=robots.size() && actor.known==0 && actor.unknown==0,"fixed joint support/training identity differs");
        check(actor.decode({"EA",rat(31,25),rat(63,50),1,true})==-1 && actor.decode({"EA",rat(1083441,1000000),rat(1083442,1000000),2,true})==-1,
              "END-only unknown support guessed a class");
        for(const auto& robot:robots){check(robot.heads.size()>=128,"R7 ongoing FIFO reservoir required");++target_tasks;}
        S scheduler("empty-joint",rat(0));S::Delta d{{"empty-joint","resident-joint",{},{},{}},rat(0),{},{}};
        for(const auto& r:robots){const auto c=cell_name(r.x,r.y);check(d.structure.owners.emplace(c,std::make_shared<const I::Owner>(I::Owner{
            "resident-"+std::to_string(r.agent),"agent-"+std::to_string(r.agent),"",false})).second,"joint initial residents overlap");}
        auto initial=scheduler.prepare(d);scheduler.commit(std::move(initial));owner.reset(new P(scheduler,{}));replenish();rebuild_demands();start_ready();frame();
    }
    void run() {
        bool deadlock=false;unsigned turns=0;
        while(true){check(++turns<16384,"joint event bound");

            R next=horizon;bool pending=false,query_slot=false,feedback_slot=false,wait_slot=false;
            auto earlier=[&](const R& value){if(O::cmp(value,clock)<=0)return;
                if(O::cmp(value,next)<0)next=value;
                pending=true;};
            for(const auto& m:moves){if(!m->physical){const auto s=m->controller.snapshot();earlier(O::add(s.segment_start(),s.segment().duration()));}
                if(m->physical&&!m->native)earlier(*m->delivery);
                if(!opportunity_consumed.count(m->key))earlier(O::add(m->launch,rat(3,4)));}
            for(const auto& r:robots)if(r.wait_until)earlier(*r.wait_until);
            if(!pending){replenish();rebuild_demands();start_ready();bool work=false;for(const auto& m:moves)if(!m->native)work=true;if(work)continue;deadlock=true;event("joint_deadlock",std::to_string(served));break;}
            for(const auto& m:moves)if(!opportunity_consumed.count(m->key) && same(O::add(m->launch,rat(3,4)),next))query_slot=true;
            for(const auto& m:moves)if(m->physical&&!m->native&&same(*m->delivery,next))feedback_slot=true;
            for(const auto& r:robots)if(r.wait_until&&same(*r.wait_until,next))wait_slot=true;
            advance_physics(next);service_heads();deliver();
            if(query_slot||feedback_slot||wait_slot)queries(query_slot?"public_age_gate":feedback_slot?"normal_END_demand_update":"public_WAIT_demand_update");
            frame();
            if(same(clock,horizon))break;
        }
        for(const auto& r:robots)if(!r.served)flow_sum=O::add(flow_sum,O::sub(horizon,r.released));
        std::cout<<"{\"event\":\"joint_summary\",\"status\":\"passed\",\"served\":"<<served<<",\"task_count\":"<<target_tasks<<",\"robot_count\":"<<robots.size()<<",\"queries\":"<<asked.size()
                 <<",\"capacity\":"<<capacity<<",\"policy\":\""<<policy<<"\",\"started_MOVEs\":"<<started
                 <<",\"delivered_END\":"<<feedback<<",\"deadlock\":"<<(deadlock?"true":"false")<<",\"last_clock\":";bound3(clock);
        std::cout<<",\"service_time_sum\":";bound3(completion_sum);std::cout<<",\"released_restricted_flow_sum\":";bound3(flow_sum);std::cout<<",\"horizon\":";bound3(horizon);std::cout<<",\"official_plan_calls\":"<<plan_round;
        std::cout<<",\"uncompleted_heads\":"<<(target_tasks-served)<<",\"max_candidates\":"<<max_candidates<<",\"eligible_opportunities\":"<<eligible_opportunities<<",\"native_checks\":"<<checks
                 <<",\"joint_shared_owner_state\":true,\"published_external_comparison\":false,\"production_COST\":false}\n";
    }
};
}
int main(int argc,char** argv) {
    try {check(argc==4,"joint input policy capacity arguments required");const unsigned b=static_cast<unsigned>(std::stoul(argv[3]));check(b<=64,"joint capacity outside contract");
        const std::string p=argv[2];check(p=="WAIT"||p=="condition"||p=="macro_C"||p=="macro_LD"||p=="alwaysLD"||p=="budget_lookup"||p=="full"||p=="no_history_prob","unknown joint policy");
        World3 world(argv[1],p,b);world.run();return 0;}
    catch(const std::exception& e){std::cerr<<"joint native failed after "<<checks<<" checks: "<<e.what()<<'\n';return 1;}
}
