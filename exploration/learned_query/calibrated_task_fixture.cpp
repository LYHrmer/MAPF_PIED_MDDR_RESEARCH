// Historical-duration calibration/learning successor; old fixtures unchanged.
#define main preserved_legal_and_task_entry
#include "legal_and_fixture.cpp"
#undef main
#include <set>

namespace {
enum class TaskPolicy { Srdc, RR, AdmissionOne, AdmissionPair,
                        CompletionOne, CompletionPair, CompletionPairLong, Wait };
const char* policy_name(TaskPolicy p) {
    switch (p) {
    case TaskPolicy::Srdc: return "original_srdc_unpriced";
    case TaskPolicy::RR: return "original_rr";
    case TaskPolicy::AdmissionOne: return "unit_admission_one";
    case TaskPolicy::AdmissionPair: return "unit_admission_pair";
    case TaskPolicy::CompletionOne: return "nominal_completion_one_window6";
    case TaskPolicy::CompletionPair: return "nominal_completion_pair_window6";
    case TaskPolicy::CompletionPairLong: return "nominal_completion_pair_window7";
    case TaskPolicy::Wait: return "no_progress_queries";
    }
    throw std::logic_error("unknown task policy");
}
void interval(const R& x) {
    check(O::cmp(x, rat(0)) >= 0 && O::cmp(x, rat(64)) < 0, "display range");
    long lo = 0, hi = 64000000;
    while (hi - lo > 1) {
        const long mid = lo + (hi - lo) / 2;
        if (O::cmp(rat(mid, 1000000), x) <= 0) lo = mid; else hi = mid;
    }
    std::cout << "{\"lower\":" << lo << ",\"upper\":"
              << (same(x, rat(lo, 1000000)) ? lo : hi) << ",\"denominator\":1000000}";
}
R blocker_duration_prior(const R& length) { return O::sqrt(O::mul(rat(3), length)); }
struct DurationModel {
    R alpha;
    std::string name;
    R predict(const R& length) const { return O::sqrt(O::mul(alpha,length)); }
};
R end_delivery_prior() { return rat(1, 4); }
R first_service_at_or_after(const R& arrival) {
    long row = 8; // Public periodic service schedule; NO evaluation stop input.
    while (O::cmp(rat(row), arrival) < 0) {
        ++row; check(row < 64, "nominal service outside finite display domain");
    }
    return rat(row);
}
std::unique_ptr<P> task_initial(TaskPolicy policy) {
    auto baseline = initial();
    const auto state = baseline->view();
    S s("task-empty", rat(0), policy == TaskPolicy::RR ?
        pie_query::QueryPolicy::RoundRobin : pie_query::QueryPolicy::Srdc);
    S::Delta d{{"task-empty", "task-initial", {}, {}, {}}, rat(0), {}, {}};
    for (const auto& a : state.structure().actions) d.structure.actions.emplace(a.first, a.second->input);
    for (const auto& o : state.structure().owners)
        d.structure.owners.emplace(o.first, std::make_shared<const I::Owner>(o.second));
    for (const auto& q : state.structure().demands) d.structure.demands.emplace(q.first, q.second->input);
    auto update = s.prepare(d); s.commit(std::move(update));
    pie_query::Map<P::SnapshotIds> ids;
    for (const auto& a : d.structure.actions)
        ids.emplace(a.first, P::SnapshotIds{a.first + "-task-seed", a.first + "-task-current", "", ""});
    return std::unique_ptr<P>(new P(s, ids));
}
bool available(const P::View& v, const I::Demand& d) {
    if (!d.non_owner_eligible) return false;
    for (const auto& cell : d.resources) {
        const auto o = v.structure().owners.find(cell);
        if (o != v.structure().owners.end() && o->second.agent != d.agent) return false;
    }
    return true;
}
bool unit_clears(const I::State& s, const I::Relation& r,
                 const std::set<std::string>& observed) {
    if (!r.retirable || !r.threshold || !observed.count(r.action)) return false;
    const auto& a = *s.actions.at(r.action)->input;
    return a.eligible && a.epsilon && O::cmp(O::sub(a.b, *a.epsilon), *r.threshold) > 0;
}
unsigned admission_value(const I::State& s, const std::set<std::string>& selected) {
    unsigned n = 0;
    for (const auto& d : s.demands) {
        bool all = d.second->input->non_owner_eligible && !d.second->relations.empty();
        for (const auto& r : d.second->relations) if (!unit_clears(s, r, selected)) all = false;
        if (all) ++n;
    }
    return n;
}
R partial_value(const I::State& s, const std::string& key) {
    R result = rat(0);
    for (const auto& d : s.demands) {
        if (!d.second->input->non_owner_eligible || d.second->relations.empty()) continue;
        for (const auto& r : d.second->relations)
            if (unit_clears(s, r, {key})) result = O::add(result, rat(1, d.second->relations.size()));
    }
    return result;
}
using PublicPlans = pie_query::Map<std::vector<R>>;

// Only committed relations, public current-task lengths, a declared nominal
// controller prior and public opportunities enter this predictor. It sees no
// Controller, world task queue, actual finish, future assigned task or stop time.
// Waiting demands here have pairwise disjoint sweeps. This is a finite policy
// probe, not a general collision-aware rollout or an optimality claim.
unsigned completion_value(const I::State& s, const PublicPlans& plans,
                          const std::vector<std::string>& sequence,
                          const std::vector<R>& opportunities, const R& now,
                          const R& window, const DurationModel& model) {
    unsigned value = 0;
    for (const auto& d : s.demands) {
        if (!d.second->input->non_owner_eligible) continue;
        R start = now; bool possible = true;
        for (const auto& r : d.second->relations) {
            if (!r.retirable || !r.threshold) { possible = false; break; }
            const auto& a = *s.actions.at(r.action)->input;
            // Nominal END delivery is available even without a progress query.
            // Initial blockers' nominal launch at 0 is public fixture input.
            R release = O::add(blocker_duration_prior(a.geometry.length()), end_delivery_prior());
            for (std::size_t k = 0; k < sequence.size(); ++k)
                if (sequence[k] == r.action && unit_clears(s, r, {r.action}) &&
                    O::cmp(opportunities[k], release) < 0) release = opportunities[k];
            if (O::cmp(release, start) > 0) start = release;
        }
        if (!possible) continue;
        const auto& lengths = plans.at(d.first);
        R arrival = start;
        for (std::size_t k = 0; k < lengths.size(); ++k) {
            arrival = O::add(arrival, model.predict(lengths[k]));
            if (k + 1 < lengths.size()) arrival = O::add(arrival, end_delivery_prior());
        }
        // Service need not await final END/READY delivery.
        if (O::cmp(first_service_at_or_after(arrival), O::add(now, window)) <= 0) ++value;
    }
    return value;
}
std::string choose_probe(const P::View& view, const PublicPlans& plans, TaskPolicy rule,
                         const std::vector<R>& opportunities, const R& at,
                         const DurationModel& model) {
    if (rule == TaskPolicy::Wait) return "";
    const auto& state = view.structure();
    std::vector<std::string> keys;
    for (const auto& a : state.actions) if (a.second->input->eligible) keys.push_back(a.first);
    check(!keys.empty(), "finite query candidates absent");
    const bool admission = rule == TaskPolicy::AdmissionOne || rule == TaskPolicy::AdmissionPair;
    if (admission) {
        std::string best; unsigned score = 0; R partial = rat(0);
        if (rule == TaskPolicy::AdmissionPair && opportunities.size() == 2) {
            for (const auto& a : keys) for (const auto& b : keys) {
                if (a == b) continue;
                const auto v = admission_value(state, {a,b});
                if (best.empty() || v > score) { best = a; score = v; }
            }
            return best;
        }
        for (const auto& a : keys) {
            const auto v = admission_value(state, {a}); const R p = partial_value(state, a);
            if (best.empty() || v > score || (v == score && O::cmp(p, partial) > 0)) {
                best = a; score = v; partial = p;
            }
        }
        return best;
    }
    const unsigned depth = rule == TaskPolicy::CompletionOne ? 1u : static_cast<unsigned>(opportunities.size());
    const R window = rule == TaskPolicy::CompletionPairLong ? rat(7) : rat(6);
    keys.insert(keys.begin(), ""); // WAIT is a real option; no implicit query.
    unsigned best_value = 0, best_queries = 3; std::vector<std::string> best;
    auto consider = [&](const std::vector<std::string>& sequence) {
        const unsigned v = completion_value(state, plans, sequence, opportunities, at, window,model);
        unsigned count = 0; for (const auto& key : sequence) if (!key.empty()) ++count;
        // Query count is a diagnostic tie-break, NOT a fabricated paid quote.
        if (best.empty() || v > best_value || (v == best_value && count < best_queries)) {
            best = sequence; best_value = v; best_queries = count;
        }
    };
    for (const auto& a : keys) {
        if (depth == 1) consider({a});
        else for (const auto& b : keys) if (a.empty() || a != b) consider({a,b});
    }
    check(!best.empty(), "completion search produced no action");
    std::cout << "{\"event\":\"completion_forecast\",\"rolling_window\":"
              << exact(window) << ",\"predicted_pending_task_completions\":" << best_value
              << ",\"diagnostic_query_count\":" << best_queries << "}\n";
    return best.front();
}

struct Leg { std::string key; long from, to, y; };
struct Lane {
    std::string key, agent;
    long y, original_start, original_end, physical_x, goal;
    unsigned task = 1, next_leg = 0, served = 0;
    bool assigned = true, ready = true;
    std::vector<Leg> plan;
    R assigned_at;
    Lane(const std::string& id, long row, long begin, long end)
        : key(id), agent("agent-" + id), y(row), original_start(begin), original_end(end),
          physical_x(begin), goal(end+1), plan{{id,begin,end,row},{id+"-task1-leg2",end,end+1,row}},
          assigned_at(rat(0)) {}
};
struct Moving {
    std::string key, agent;
    G geometry;
    Controller controller;
    int lane;
    bool physical_end = false, native_end = false;
    std::shared_ptr<const R> ended, delivery;
    Moving(const std::string& id, const std::string& owner, const G& g, const R& at, int n,
           const R& private_eta)
        : key(id), agent(owner), geometry(g),
          controller({rat(1),rat(2),rat(6),rat(1)},g.length(),at,g.length(),private_eta,id), lane(n) {
        check(controller.run(at), "new original MOVE did not RUN");
    }
};
struct TaskResult { std::vector<std::string> queries; std::vector<unsigned> curve; unsigned served_before_ready; };
class TaskWorld {
    const R requester_eta;
    const DurationModel duration_model;
    const std::string evaluation_id;
    std::unique_ptr<P> p;
    std::vector<Lane> lanes;
    std::vector<std::unique_ptr<Moving>> moves;
    std::set<std::string> serviced;
    std::vector<std::string> queried;
    unsigned revision = 0, before_ready = 0, task_deliveries = 0, started_moves = 0;
    std::vector<unsigned> curve;
    R clock = rat(0);

    S::Delta change(const std::string& tag) {
        return {{p->view().structure().view_id, tag+"-"+std::to_string(++revision), {},{},{}},clock,{}, {}};
    }
    bool active(unsigned lane) const {
        for (const auto& m : moves) if (m->lane == static_cast<int>(lane) && !m->native_end) return true;
        return false;
    }
    void event(const char* kind, const std::string& id) {
        std::cout << "{\"event\":\"" << kind << "\",\"id\":\"" << id << "\",\"at\":";
        interval(clock); std::cout << "}\n";
    }
    void advance(const R& at) {
        clock = at;
        for (auto& m : moves) {
            if (m->physical_end) continue;
            m->controller.advance_to(at);
            const auto s = m->controller.snapshot();
            if (!s.closed()) continue;
            check(s.move_id() == m->key && same(s.state().s,s.length()) && same(s.state().v,rat(0)),
                  "physical END lacks original endpoint at rest");
            m->physical_end = true; m->ended = std::make_shared<const R>(at);
            m->delivery = std::make_shared<const R>(O::add(at,end_delivery_prior()));
            if (m->lane >= 0) {
                auto& l = lanes.at(static_cast<unsigned>(m->lane));
                check(l.next_leg > 0, "END without a planned current leg");
                l.physical_x = l.plan.at(l.next_leg-1).to;
            }
            event("physical_original_end",m->key);
        }
    }
    void deliver_ends() {
        for (auto& m : moves) {
            if (!m->physical_end || m->native_end || !same(*m->delivery,clock)) continue;
            const auto before = p->view();
            const auto endpoint = m->geometry.n_mask(m->geometry.length(),m->geometry.length());
            for (const auto& cell : endpoint.mask())
                check(before.structure().owners.at(cell).action == m->key, "END endpoint lost ownership");
            auto delta = change("native-END"); delta.structure.actions.emplace(m->key,nullptr);
            // END itself releases the old responsibility. No extra POSITION
            // query is silently added; endpoint resources become residents.
            for (const auto& own : before.structure().owners) if (own.second.action == m->key) {
                if (std::find(endpoint.mask().begin(),endpoint.mask().end(),own.first) != endpoint.mask().end())
                    delta.structure.owners.emplace(own.first,std::make_shared<const I::Owner>(
                        I::Owner{"resident-"+m->agent,m->agent,"",false}));
                else delta.structure.owners.emplace(own.first,nullptr);
            }
            auto prepared = p->prepare_admitted_update(delta,{}); p->commit(std::move(prepared));
            check(!p->view().structure().actions.count(m->key), "END retained old action");
            m->native_end = true;
            event("native_end_ownership_handoff",m->key);
            if (m->lane >= 0) {
                auto& l = lanes.at(static_cast<unsigned>(m->lane));
                check(!l.ready, "READY consumed twice"); l.ready = true;
                event("native_ready_consumed",m->key);
            }
        }
    }
    bool service_true(unsigned n) const {
        const auto& l = lanes.at(n);
        if (!l.assigned || l.physical_x != l.goal) return false;
        // Active motion may have physically ENDed while its software delivery
        // is pending. That stationary original endpoint can already serve.
        for (const auto& m : moves) if (m->lane == static_cast<int>(n) && !m->native_end)
            if (!m->physical_end || !same(m->controller.snapshot().state().v,rat(0))) return false;
        // Actual z=0 witness, full square footprint half-width 1/10, closed
        // task service square half-width 1/5. Test all four actual vertices.
        for (long dx : {-1L,1L}) for (long dy : {-1L,1L}) {
            const R x = O::add(rat(l.physical_x),rat(dx,10));
            const R y = O::add(rat(l.y),rat(dy,10));
            if (O::cmp(x,O::sub(rat(l.goal),rat(1,5))) < 0 ||
                O::cmp(x,O::add(rat(l.goal),rat(1,5))) > 0 ||
                O::cmp(y,O::sub(rat(l.y),rat(1,5))) < 0 ||
                O::cmp(y,O::add(rat(l.y),rat(1,5))) > 0) return false;
        }
        return true;
    }
    void service_row() {
        std::vector<unsigned> successes;
        // First evaluate every OLD head, then apply services and replenishment.
        for (unsigned n=0; n<lanes.size(); ++n) if (service_true(n)) successes.push_back(n);
        for (const auto n : successes) {
            auto& l=lanes[n]; const std::string task=l.key+"-task"+std::to_string(l.task);
            check(serviced.insert(task).second, "task counted twice");
            check(l.next_leg == l.plan.size(), "intermediate MOVE counted as a task");
            if (!l.ready) ++before_ready;
            ++l.served; l.assigned=false;
            std::cout << "{\"event\":\"task_service\",\"task\":\"" << task
                      << "\",\"agent\":\"" << l.agent << "\",\"at\":";
            interval(clock); std::cout << ",\"assigned_at\":"; interval(l.assigned_at);
            std::cout << ",\"before_native_ready\":" << (!l.ready ? "true" : "false") << "}\n";
        }
        // This fixture's private fixed source contains three goals per agent.
        // Future tasks only become public after this world-row replenishment.
        for (const auto n : successes) {
            auto& l=lanes[n]; if (l.task == 3) continue;
            ++l.task; l.assigned=true; l.assigned_at=clock;
            l.goal=l.task == 2 ? l.original_end : l.original_end+1;
            const std::string key=l.key+"-task"+std::to_string(l.task)+"-leg1";
            l.plan={{key,l.physical_x,l.goal,l.y}}; l.next_leg=0;
            event("task_assigned",l.key+"-task"+std::to_string(l.task));
            ++task_deliveries; event("native_task_knowledge_delivered",key);
        }
        curve.push_back(static_cast<unsigned>(serviced.size()));
    }
    void start_ready() {
        for (unsigned n=0; n<lanes.size(); ++n) {
            auto& l=lanes[n];
            if (!l.assigned || !l.ready || active(n) || l.next_leg == l.plan.size()) continue;
            const auto& leg=l.plan.at(l.next_leg);
            check(l.physical_x == leg.from, "successor MOVE teleported its start");
            const G g=geometry(leg.key,leg.from,leg.y,leg.to,leg.y);
            const auto full=g.n_mask(rat(0),g.length());
            if (!p->view().structure().demands.count(leg.key)) {
                auto request=change("request");
                request.structure.demands.emplace(leg.key,std::make_shared<const I::Demand>(
                    I::Demand{l.agent,"",full.mask(),clock,true}));
                auto pending=p->prepare_admitted_update(request,{}); p->commit(std::move(pending));
            }
            const auto before=p->view();
            if (!available(before,*before.structure().demands.at(leg.key)->input)) continue;
            const auto residence=g.n_mask(rat(0),rat(0));
            for (const auto& cell : residence.mask()) {
                const auto& own=before.structure().owners.at(cell);
                check(own.agent == l.agent && !own.geometric && own.action.empty(), "start lacks resident/READY handoff");
            }
            auto grant=change("grant"); auto a=std::make_shared<I::Action>(*action(l.agent,g));
            a->eligible=false; grant.structure.actions.emplace(leg.key,a);
            for (const auto& cell : full.mask()) {
                const auto own=before.structure().owners.find(cell);
                check(own == before.structure().owners.end() || own->second.agent == l.agent, "grant collided");
                grant.structure.owners.emplace(cell,std::make_shared<const I::Owner>(
                    I::Owner{leg.key,l.agent,leg.key,true}));
            }
            grant.structure.demands.emplace(leg.key,nullptr);
            auto pending=p->prepare_admitted_update(grant,{{leg.key,{leg.key+"-seed",leg.key+"-current","",""}}});
            p->commit(std::move(pending)); l.ready=false; ++l.next_leg; ++started_moves;
            moves.emplace_back(new Moving(leg.key,l.agent,g,clock,static_cast<int>(n),requester_eta));
            event("original_move_started",leg.key);
        }
    }
    PublicPlans public_plans() const {
        PublicPlans result;
        for (const auto& l : lanes) {
            if (!l.assigned || l.next_leg == l.plan.size()) continue;
            const auto& first=l.plan.at(l.next_leg);
            if (!p->view().structure().demands.count(first.key)) continue;
            std::vector<R> lengths;
            for (std::size_t k=l.next_leg;k<l.plan.size();++k) {
                const R delta=O::sub(rat(l.plan[k].to),rat(l.plan[k].from));
                lengths.push_back(O::cmp(delta,rat(0)) < 0 ? O::sub(rat(0),delta) : delta);
            }
            result.emplace(first.key,std::move(lengths));
        }
        return result;
    }
    void query_opportunity(TaskPolicy rule, unsigned step) {
        const auto before=p->view(); std::string key;
        if (rule == TaskPolicy::Srdc || rule == TaskPolicy::RR) {
            const auto chosen=p->choose(clock);
            check(chosen.kind() == pie_query::ChoiceKind::RoundRobin && chosen.score(), "unpriced original did not use RR");
            key=chosen.score()->action;
            auto pub=p->prepare_query_publication(chosen,{chosen.view(),key,chosen.score()->source,
                "native-task-query-not-AUTH",chosen.generation(),clock});
            p->commit(std::move(pub));
        } else {
            const std::vector<R> opportunities=step == 0 ? std::vector<R>{rat(5,2),rat(11,4)} : std::vector<R>{rat(11,4)};
            key=choose_probe(before,public_plans(),rule,opportunities,clock,duration_model);
            check(p->view().same_identity(before), "prediction mutated actual owner state");
        }
        if (key.empty()) { event("no_query",std::to_string(step)); return; }
        check(key == "A" || key == "B" || key == "C", "queried outside finite eligible blocker set");
        check(std::find(queried.begin(),queried.end(),key) == queried.end(), "repeated query");
        event("query_selected",key);
        // Physical state enters the certificate ONLY after selection.
        Moving& m=*moves.at(static_cast<unsigned>(key[0]-'A'));
        query(*p,m.controller,clock,"task-probe-"+key);
        queried.push_back(key);
        auto seen=change("observed"); auto a=std::make_shared<I::Action>(*p->view().structure().actions.at(key)->input);
        a->eligible=false; seen.structure.actions.emplace(key,a);
        auto pending=p->prepare_admitted_update(seen,{}); p->commit(std::move(pending));
        for (unsigned k=0;k<3;++k) {
            const auto& id=moves[k]->key;
            if (std::find(queried.begin(),queried.end(),id) == queried.end())
                check(same(p->view().structure().actions.at(id)->input->q,rat(0)), "unqueried progress leaked");
        }
    }
public:
    TaskWorld(TaskPolicy policy, const R& actual_eta, const DurationModel& model,
              const std::string& run_id) : requester_eta(actual_eta), duration_model(model),
        evaluation_id(run_id), p(task_initial(policy)),
        lanes{Lane("D1",1,-2,4),Lane("D2",2,-2,4),Lane("D3",1,6,10)} {
        for (const std::string key : {"A","B","C"}) moves.emplace_back(new Moving(key,"agent-"+key,blocker(key),rat(0),-1,rat(-1)));
        // Pairwise disjoint request sweeps justify the finite independent
        // admission forecast. Production rollout must check general conflicts.
        const auto v=p->view(); std::set<std::string> requested;
        for (const auto& d : v.structure().demands) for (const auto& r : d.second->input->resources)
            check(requested.insert(r).second,"fixture demands overlap each other");
    }
    TaskResult run(TaskPolicy policy) {
        std::cout << "{\"event\":\"policy_begin\",\"policy\":\"" << policy_name(policy)
                  << "\",\"run_id\":\"" << evaluation_id << "\",\"predictor\":\""
                  << duration_model.name << "\"}\n";
        unsigned query_step=0; long service=8; unsigned events=0;
        // The evaluation stop is deliberately only in the world event loop.
        // Neither choose_probe nor completion_value receives it.
        while (service <= 16) {
            check(++events < 300, "finite world failed to progress");
            R next=rat(service);
            auto earlier=[&](const R& t) { if (O::cmp(t,next)<0) next=t; };
            if (query_step<2) earlier(query_step == 0 ? rat(5,2) : rat(11,4));
            for (const auto& m : moves) {
                if (!m->physical_end) {
                    const auto s=m->controller.snapshot(); earlier(O::add(s.segment_start(),s.segment().duration()));
                } else if (!m->native_end) earlier(*m->delivery);
            }
            check(O::cmp(next,clock)>0,"event loop repeated a time");
            advance(next); deliver_ends();
            if (same(clock,rat(service))) { service_row(); ++service; }
            if (query_step<2 && same(clock,query_step == 0 ? rat(5,2) : rat(11,4)))
                query_opportunity(policy,query_step++);
            start_ready();
        }
        check(serviced.size()==9 && task_deliveries==6 && started_moves==12,"task loop did not execute all assigned work");
        for (const auto& m : moves) check(m->physical_end && m->native_end,"end/READY lifecycle incomplete");
        check(p->view().structure().actions.empty() && p->view().structure().demands.empty(),"old MOVE or request survived final handoff");
        for (const auto& l : lanes) {
            check(l.served==3 && !l.assigned && l.ready,"final task/resident state invalid");
            const G g=geometry(l.key+"-final-check",l.original_end,l.y,l.original_end+1,l.y);
            const auto resident=g.n_mask(g.length(),g.length());
            for (const auto& cell : resident.mask()) {
                const auto& own=p->view().structure().owners.at(cell);
                check(own.agent==l.agent && !own.geometric && own.action.empty(),"finished agent lost resident footprint");
            }
        }
        std::cout << "{\"event\":\"policy_result\",\"policy\":\"" << policy_name(policy)
                  << "\",\"run_id\":\"" << evaluation_id << "\",\"predictor\":\"" << duration_model.name
                  << "\",\"queries\":[";
        for (std::size_t k=0;k<queried.size();++k) { if(k) std::cout<<','; std::cout<<'"'<<queried[k]<<'"'; }
        std::cout << "],\"service_times\":[8,9,10,11,12,13,14,15,16],\"completed_tasks\":[";
        for (std::size_t k=0;k<curve.size();++k) { if(k) std::cout<<','; std::cout<<curve[k]; }
        std::cout << "],\"served_before_native_ready\":" << before_ready
                  << ",\"original_requester_moves\":" << started_moves << ",\"final_tasks\":" << serviced.size() << "}\n";
        return {queried,curve,before_ready};
    }
};
struct DeliveredDuration {
    std::string run_id, move_id;
    R length, start, end, received;
};
DeliveredDuration historical_move(const std::string& id, const R& length,
                                  const R& private_eta) {
    const std::string move_id=id+"-move";
    Controller controller({rat(1),rat(2),rat(6),rat(1)},length,rat(0),length,private_eta,move_id);
    check(controller.run(rat(0)),"historical native RUN failed");
    unsigned boundaries=0;
    while (!controller.snapshot().closed()) {
        check(++boundaries<=3,"history control did not end");
        const auto s=controller.snapshot();
        controller.advance_to(O::add(s.segment_start(),s.segment().duration()));
    }
    const auto s=controller.snapshot();
    check(s.move_id()==move_id && same(s.state().s,length) && same(s.state().v,rat(0)),"invalid historical original END");
    const R at=s.time();
    // Only the returned END payload and its received time leave this generator;
    // neither eta nor the private Controller is passed to fit/calibration.
    DeliveredDuration row{id,move_id,length,rat(0),at,O::add(at,end_delivery_prior())};
    std::cout << "{\"event\":\"historical_native_END_delivered\",\"run_id\":\"" << id
              << "\",\"move_id\":\"" << row.move_id << "\",\"length\":" << exact(length)
              << ",\"started\":"; interval(row.start);
    std::cout << ",\"ended\":"; interval(row.end);
    std::cout << ",\"received\":"; interval(row.received);
    std::cout << ",\"full_cap_uninterrupted\":true,\"motion_profile\":\"shared_requester_profile\""
              << ",\"clock_domain\":\"completed_independent_run\"}\n";
    return row;
}
DurationModel fit_duration(const std::vector<DeliveredDuration>& rows) {
    check(rows.size()>=2,"fit needs independent historical runs");
    std::set<std::string> ids; R numerator=rat(0),denominator=rat(0);
    for (const auto& row : rows) {
        check(ids.insert(row.run_id).second,"duplicated training run");
        check(O::cmp(row.received,row.end)>0 && O::cmp(row.end,row.start)>0,
              "training label was not delivered");
        const R duration=O::sub(row.end,row.start);
        numerator=O::add(numerator,O::mul(row.length,O::mul(duration,duration)));
        denominator=O::add(denominator,O::mul(row.length,row.length));
    }
    // Exact one-parameter least squares for D^2 = alpha L, intercept fixed 0.
    // All normalization/labels are historical. This is a deliberately small
    // fitted regression, not a classifier, a neural net, or a world model.
    return {O::div(numerator,denominator),"historical_least_squares"};
}
DurationModel calibrate_last(const std::vector<DeliveredDuration>& rows) {
    const auto& row=rows.back(); const R d=O::sub(row.end,row.start);
    return {O::div(O::mul(d,d),row.length),"analytic_last_END_calibration"};
}
void task_comparison() {
    for (const long actual_eta : {-1L,1L}) {
        const std::string condition=actual_eta == -1 ? "stationary_slow" : "stationary_fast";
        // Separate finished historical runs are available BEFORE test runs.
        // Stationarity across them is an explicit artificial premise.
        const std::vector<DeliveredDuration> history={
            historical_move(condition+"-train1",rat(1),rat(actual_eta)),
            historical_move(condition+"-train2",rat(2),rat(actual_eta))};
        const DurationModel learned=fit_duration(history), calibrated=calibrate_last(history);
        const std::vector<DurationModel> models={{rat(3),"frozen_nominal"},calibrated,learned,
                                                {rat(3),"original_srdc_unpriced"},{rat(3),"no_query"}};
        std::cout << "{\"event\":\"fit_result\",\"condition\":\"" << condition
                  << "\",\"training_rows\":2,\"fitted_alpha\":"; interval(learned.alpha);
        std::cout << ",\"same_as_last_END_calibration\":" << (same(learned.alpha,calibrated.alpha)?"true":"false") << "}\n";
        std::vector<TaskResult> results;
        for (std::size_t k=0;k<models.size();++k) {
            const TaskPolicy policy=k==3 ? TaskPolicy::Srdc : k==4 ? TaskPolicy::Wait : TaskPolicy::CompletionPair;
            const std::string run_id=condition+"-test-"+models[k].name;
            for (const auto& row : history) check(run_id != row.run_id,"test run in training labels");
            TaskWorld world(policy,rat(actual_eta),models[k],run_id);
            results.push_back(world.run(policy));
        }
        check(results[1].queries==results[2].queries && results[1].curve==results[2].curve,
              "calibration/regression disagreement on homogeneous exact histories");
        // Do NOT require improvement: actual curves and query counts are output
        // even when the model loses. Final nine-task integrity is checked above.
    }
    std::cout << "{\"event\":\"summary\",\"status\":\"passed\",\"checks\":" << checks
              << ",\"finite_task_service\":true,\"production_AUTH\":false,\"full_paid_cost\":false"
              << ",\"learning\":true,\"learning_scope\":\"exact_one_parameter_regression_on_native_historical_END\""
              << ",\"independent_learning_advantage_claim\":false,\"lifelong_performance_claim\":false}\n";
}
} // namespace
int main() {
    try { task_comparison(); return 0; }
    catch (const std::exception& e) { std::cerr<<"task continuation failed after "<<checks<<" checks: "<<e.what()<<'\n'; return 1; }
}
