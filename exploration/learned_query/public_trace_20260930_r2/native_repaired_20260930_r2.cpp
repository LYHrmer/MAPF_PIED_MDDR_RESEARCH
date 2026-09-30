// Actual author-map crops, original native exact controller and Geometry.
#define main preserved_legal_fixture_entry
#include "../legal_and_fixture.cpp"
#undef main
#include <fstream>
#include <sstream>
#include <map>

namespace {
void bound(const R& x) {
    check(O::cmp(x,rat(0))>=0 && O::cmp(x,rat(8))<0,"native bound range");
    long lo=0,hi=8000000;
    while(hi-lo>1) { const long mid=lo+(hi-lo)/2;
        if(O::cmp(rat(mid,1000000),x)<=0)lo=mid;else hi=mid; }
    std::cout<<"{\"lower\":"<<lo<<",\"upper\":"<<(same(x,rat(lo,1000000))?lo:hi)
             <<",\"denominator\":1000000}";
}
R finish(Controller& c) {
    unsigned n=0;
    while(!c.snapshot().closed()) {
        check(++n<=4,"original native controller boundary limit");
        const auto s=c.snapshot();c.advance_to(O::add(s.segment_start(),s.segment().duration()));
    }
    check(same(c.snapshot().state().s,c.snapshot().length()) && same(c.snapshot().state().v,rat(0)),
          "original full MOVE did not end at rest");
    return c.snapshot().time();
}
struct Move { unsigned agent;long sx,sy,ex,ey,eta; };
struct Pair { unsigned id,a,b;long sx,sy,ex,ey,bx,by,task;bool terminal; };
G crop_geometry(const Pair& p,const std::string& key,bool source) {
    std::vector<G::Resource> cells;
    const long xmin=std::min({p.sx,p.ex,p.bx})-1,xmax=std::max({p.sx,p.ex,p.bx})+1;
    const long ymin=std::min({p.sy,p.ey,p.by})-1,ymax=std::max({p.sy,p.ey,p.by})+1;
    for(long x=xmin;x<=xmax;++x)for(long y=ymin;y<=ymax;++y)
        cells.push_back({"cell-"+std::to_string(x)+"-"+std::to_string(y),{square(rat(x),rat(y),rat(1,2))}});
    return G({{"public-PIED-74cfba3-R1","exact-flint","column-row-plane","one-grid-unit",key},
        {rat(source?p.sx:p.bx),rat(source?p.sy:p.by)},
        {rat(source?p.ex:p.sx),rat(source?p.ey:p.sy)},
        {square(rat(0),rat(0),rat(1,10))},
        {{rat(-1,20),rat(-1,20)},{rat(1,20),rat(1,20)}},cells},true);
}
std::shared_ptr<const I::Action> crop_action(const std::string& who,const G& g) {
    return std::make_shared<const I::Action>(I::Action{who,"native-crop-admitted-not-AUTH",
        "fixed-reference-profile",g,rat(0),g.length(),std::make_shared<const R>(rat(1,10)),true});
}
std::unique_ptr<P> pair_owner(const G& ga,const G& gb) {
    S s("empty-crop",rat(0));
    S::Delta d{{"empty-crop","resident-crop",{},{},{}},rat(0),{},{}};
    add_owned_mask(d,ga,"source-agent",false);add_owned_mask(d,gb,"requester-agent",false);
    auto u=s.prepare(d);s.commit(std::move(u));std::unique_ptr<P> p(new P(s,{}));
    S::Delta grant{{p->view().structure().view_id,"grant-source-crop",{},{},{}},rat(0),{},{}};
    const auto key=ga.binding().move_occurrence;
    grant.structure.actions.emplace(key,crop_action("source-agent",ga));
    const auto source_full=ga.n_mask(rat(0),ga.length());
    for(const auto& cell:source_full.mask()) {
        const auto old=p->view().structure().owners.find(cell);
        check(old==p->view().structure().owners.end() || old->second.agent=="source-agent",
              "source full-cap grant overlaps requester resident");
        grant.structure.owners.emplace(cell,std::make_shared<const I::Owner>(I::Owner{key,"source-agent",key,true}));
    }
    auto granted=p->prepare_admitted_update(grant,{{key,{key+"-seed",key+"-current","",""}}});p->commit(std::move(granted));
    S::Delta wanted{{p->view().structure().view_id,"demand-crop",{},{},{}},rat(0),{},{}};
    wanted.structure.demands.emplace("B",std::make_shared<const I::Demand>(I::Demand{
        "requester-agent","",gb.n_mask(rat(0),gb.length()).mask(),rat(0),true}));
    auto requested=p->prepare_admitted_update(wanted,{});p->commit(std::move(requested));
    const auto& rel=p->view().structure().demands.at("B")->relations;
    check(rel.size()==1 && rel[0].action==key && rel[0].retirable && rel[0].threshold,
          "not a legal unique source-release crop");
    check(!ready(p->view(),"B"),"crop requester initially ready");return p;
}
void normal_end(P& p,const G& ga,const R& at) {
    const auto before=p.view();const auto key=ga.binding().move_occurrence;
    const auto endpoint=ga.n_mask(ga.length(),ga.length()).mask();
    S::Delta d{{before.structure().view_id,"normal-END-crop",{},{},{}},at,{},{}};
    d.structure.actions.emplace(key,nullptr);
    for(const auto& own:before.structure().owners)if(own.second.action==key) {
        const bool resident=std::find(endpoint.begin(),endpoint.end(),own.first)!=endpoint.end();
        d.structure.owners.emplace(own.first,resident?std::make_shared<const I::Owner>(
            I::Owner{"source-resident","source-agent","",false}):nullptr);
    }
    auto update=p.prepare_admitted_update(d,{});p.commit(std::move(update));
    check(!p.view().structure().actions.count(key),"normal END did not consume source action");
    if(p.view().structure().demands.count("B"))
        check(ready(p.view(),"B"),"normal END did not ready source follower");
}
void requester_run(P& p,const G& gb,const R& at) {
    const auto before=p.view();check(ready(before,"B"),"requester RUN without valid source release");
    S::Delta d{{before.structure().view_id,"RUN-crop",{},{},{}},at,{},{}};
    const auto key=gb.binding().move_occurrence;d.structure.actions.emplace(key,crop_action("requester-agent",gb));
    const auto requester_full=gb.n_mask(rat(0),gb.length());
    for(const auto& cell:requester_full.mask()) {
        const auto old=before.structure().owners.find(cell);
        check(old==before.structure().owners.end() || old->second.agent=="requester-agent",
              "requester acquisition overlaps retained foreign source responsibility");
        d.structure.owners.emplace(cell,std::make_shared<const I::Owner>(I::Owner{key,"requester-agent",key,true}));
    }
    d.structure.demands.emplace("B",nullptr);
    auto next=p.prepare_admitted_update(d,{{key,{key+"-seed",key+"-current","",""}}});p.commit(std::move(next));
}
void pair_episode(const Pair& data,long eta,bool probe) {
    const std::string arm=probe?"QUERY":"WAIT";
    const std::string id="pair"+std::to_string(data.id)+"-"+arm;
    const G ga=crop_geometry(data,id+"-source",true),gb=crop_geometry(data,id+"-requester",false);
    check(same(ga.length(),rat(1)) && same(gb.length(),rat(1)),"crop changed cardinal length");
    auto owner=pair_owner(ga,gb);P& p=*owner;
    const R threshold=*p.view().structure().demands.at("B")->relations.at(0).threshold;
    Controller ca({rat(1),rat(2),rat(6),rat(1)},rat(1),rat(0),rat(1),rat(eta),ga.binding().move_occurrence);
    check(ca.run(rat(0)),"crop source original RUN failed");
    ca.advance_to(rat(3,4));const R progress=ca.snapshot().state().s;
    const bool strict_prediction=O::cmp(O::sub(progress,rat(1,10)),threshold)>0;
    bool cleared=false;
    if(probe) { const auto old=p.view();query(p,ca,rat(3,4),id+"-real-POSITION");
        check(same(old.structure().actions.at(ga.binding().move_occurrence)->input->q,rat(0)),"old root changed after real query");
        cleared=ready(p.view(),"B");check(cleared==strict_prediction,"strict threshold and actual committed readiness differ"); }
    const R aend=finish(ca),delivered=O::add(aend,rat(1,4));
    const R launch=cleared?rat(3,4):delivered;
    if(cleared)requester_run(p,gb,launch);
    normal_end(p,ga,delivered);
    if(!cleared)requester_run(p,gb,launch);
    Controller cb({rat(1),rat(2),rat(6),rat(1)},rat(1),launch,rat(1),rat(0),gb.binding().move_occurrence);
    check(cb.run(launch),"crop requester original RUN failed");const R bend=finish(cb);
    const auto endpoint=gb.n_mask(rat(1),rat(1)).mask();
    for(const auto& cell:endpoint)check(p.view().structure().owners.at(cell).action==gb.binding().move_occurrence,
                                      "requester original endpoint responsibility absent");
    // z=0 actual existence witness; every actual footprint corner lies in task service square.
    for(long dx:{-1L,1L})for(long dy:{-1L,1L}) {
        const R x=O::add(rat(data.sx),rat(dx,10)),y=O::add(rat(data.sy),rat(dy,10));
        check(O::cmp(x,O::sub(rat(data.sx),rat(1,5)))>=0 && O::cmp(x,O::add(rat(data.sx),rat(1,5)))<=0 &&
              O::cmp(y,O::sub(rat(data.sy),rat(1,5)))>=0 && O::cmp(y,O::add(rat(data.sy),rat(1,5)))<=0,
              "actual requester terminal footprint outside service region");
    }
    std::cout<<"{\"event\":\"pair_episode\",\"pair\":"<<data.id<<",\"source_agent\":"<<data.a
             <<",\"requester_agent\":"<<data.b<<",\"arm\":\""<<arm<<"\",\"query_count\":"<<(probe?1:0)
             <<",\"task_id\":"<<data.task<<",\"task_service\":"<<(data.terminal?"true":"false")
             <<",\"strict_threshold\":\""<<exact(threshold)<<"\",\"epsilon\":\"1/10\",\"progress\":";
    bound(progress);std::cout<<",\"strict_cleared\":"<<(cleared?"true":"false")<<",\"source_END\":";bound(aend);
    std::cout<<",\"normal_END_delivered\":";bound(delivered);std::cout<<",\"requester_RUN\":";bound(launch);
    std::cout<<",\"requester_original_END\":";bound(bend);
    std::cout<<",\"requester_at_original_endpoint\":true,\"requester_speed_zero\":true,\"endpoint_retained\":true"
             <<",\"full_100_robot_execution\":false,\"production_AUTH\":false}\n";
}
void run_file(const char* path) {
    std::ifstream f(path);check(static_cast<bool>(f),"native phase file missing");
    std::string kind;std::map<unsigned,Move> moves;std::vector<Pair> pairs;
    while(f>>kind) {
        if(kind=="M") { Move m;f>>m.agent>>m.sx>>m.sy>>m.ex>>m.ey>>m.eta;
            check(moves.emplace(m.agent,m).second,"duplicate native phase source agent"); }
        else if(kind=="P") { Pair p;unsigned terminal;f>>p.id>>p.a>>p.b>>p.sx>>p.sy>>p.ex>>p.ey>>p.bx>>p.by>>p.task>>terminal;
            p.terminal=terminal!=0;pairs.push_back(p); }
        else throw std::runtime_error("unknown native phase record");
        check(static_cast<bool>(f),"malformed native phase record");
    }
    for(const auto& item:moves) {
        const auto& m=item.second;check(std::abs(m.sx-m.ex)+std::abs(m.sy-m.ey)==1,"native source not original cardinal MOVE");
        const std::string key="source-agent-"+std::to_string(m.agent);
        Controller c({rat(1),rat(2),rat(6),rat(1)},rat(1),rat(0),rat(1),rat(m.eta),key);
        check(c.run(rat(0)),"source dataset original RUN failed");c.advance_to(rat(3,4));const R s=c.snapshot().state().s;
        const R end=finish(c),alpha=O::mul(end,end);
        std::cout<<"{\"event\":\"source_original_END_delivered\",\"agent\":"<<m.agent
                 <<",\"alpha\":";bound(alpha);std::cout<<",\"at_query_progress\":";bound(s);
        std::cout<<",\"original_END\":";bound(end);std::cout<<",\"received\":";bound(O::add(end,rat(1,4)));
        std::cout<<",\"started\":0,\"full_cap_uninterrupted\":true,\"length\":1,\"offline_label_only\":true}\n";
    }
    for(const auto& p:pairs) { check(moves.count(p.a) && moves.count(p.b),"pair source missing original MOVE");
        check(moves.at(p.b).ex==p.sx && moves.at(p.b).ey==p.sy,"follower does not enter source origin");
        pair_episode(p,moves.at(p.a).eta,false);pair_episode(p,moves.at(p.a).eta,true); }
    std::cout<<"{\"event\":\"summary\",\"status\":\"passed\",\"source_MOVEs\":"<<moves.size()
             <<",\"pairs\":"<<pairs.size()<<",\"pair_episodes\":"<<2*pairs.size()<<",\"checks\":"<<checks<<"}\n";
}
}
int main(int argc,char** argv) {
    try { check(argc==2,"one native phase file required");run_file(argv[1]);return 0; }
    catch(const std::exception& e) { std::cerr<<"public native crop failed after "<<checks<<" checks: "<<e.what()<<'\n';return 1; }
}
