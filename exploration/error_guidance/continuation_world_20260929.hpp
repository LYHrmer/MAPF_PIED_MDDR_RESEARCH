namespace {
// Exploration successor only. Original mismatch World and all old evidence remain unchanged.
// Copies native mechanics; generalizes geometric thresholds and adds real delayed END lifecycle.
class TaskWorld {
    G blocker_;
    bool deliver_end_;
    bool end_delivered_ = false;
    std::unique_ptr<R> actual_end_;
    Controller blocker_motion_;
    std::unique_ptr<P> position_;
    R now_ = rat(0), waiting_ = rat(0), observed_lower_ = rat(0);
    R opportunity_;
    std::string opportunity_name_;
    Authorization authorization_;
    R requester_eta_, moving_ = rat(0);
    std::vector<R> move_durations_;
    unsigned serial_ = 0, observations_ = 0, edges_ = 0;
    unsigned grant_attempts_ = 0, cap_grants_ = 0, run_commands_ = 0, prefix_no_group_checks_ = 0;
    std::string tag() { return "view-" + std::to_string(++serial_); }
    S::Delta delta() {
        return {{position_->view().structure().view_id, tag(), {}, {}, {}}, now_, {}, {}};
    }
    void commit(S::Delta& d, const pie_query::Map<P::SnapshotIds>& ids = {}) {
        auto prepared = position_->prepare_admitted_update(d, ids);
        position_->commit(std::move(prepared));
    }
    void resident(const G& g) const {
        const auto occupied = g.n_mask(rat(0), rat(0));
        const auto view = position_->view();
        for (const auto& cell : occupied.mask()) {
            const auto& owner = view.structure().owners.at(cell);
            check(owner.agent == "requester" && owner.action.empty() && !owner.geometric,
                  "waiting/start footprint lacks stationary owner");
        }
    }
    bool ready(const std::string& demand) const {
        const auto view = position_->view();
        const auto& d = *view.structure().demands.at(demand);
        bool free = true;
        for (const auto& cell : d.input->resources) {
            const auto found = view.structure().owners.find(cell);
            if (found != view.structure().owners.end() && found->second.agent != d.input->agent) free = false;
        }
        check(free == d.relations.empty(), "Index readiness differs from real owner table");
        return d.input->non_owner_eligible && free;
    }
    bool attempt(const std::string& demand) {
        ++grant_attempts_;
        const auto view = position_->view();
        const auto& state = view.structure();
        // A domain check, not a fabricated GROUP_ADMIT implementation. Every
        // current request is enumerated; neither future route steps nor the
        // already GRANTED blocker can be an UNGRANTED group vertex.
        if (authorization_ == Authorization::OriginalPrefix) {
            check(state.demands.size() == 1 && state.demands.count(demand) == 1 &&
                  state.demands.at(demand)->input->requester_action.empty() &&
                  state.demands.at(demand)->input->agent == "requester",
                  "outside exact one-UNGRANTED-request prefix branch");
            check(state.actions.size() <= 1 &&
                  (state.actions.empty() || (state.actions.count("blocker") == 1 &&
                  state.actions.at("blocker")->input->agent != "requester")),
                  "prefix audit cannot treat a GRANTED blocker as an ungranted group member");
            // Original group graph uses intersections with ANOTHER request's
            // initial resident. One vertex has no such edge or cyclic SCC.
            ++prefix_no_group_checks_;
            std::cout << "{\"event\":\"prefix_no_certified_group\",\"demand\":\""
                      << demand << "\",\"ungranted_vertices\":1,\"cross_request_edges\":0,"
                      << "\"cyclic_components\":0,\"granted_blocker_excluded\":true}\n";
        }
        return ready(demand);
    }
    void observe() {
        check(observations_ == 0 && O::cmp(now_, opportunity_) <= 0, "common observation opportunity changed");
        blocker_motion_.advance_to(opportunity_);
        const auto witness = blocker_motion_.snapshot();
        check(!witness.closed() && witness.move_id() == "blocker" &&
              same(witness.length(), blocker_.length()) && same(witness.cap(), blocker_.length()),
              "observation does not belong to the active original blocker MOVE");
        const auto before = position_->view();
        const auto& a = *before.structure().actions.at("blocker")->input;
        check(same(a.q, rat(0)), "uncertified blocker truth entered committed progress");
        // The exact source interval is [s,s]. No predicted/expected lower is used.
        Certificate c{{"blocker", a.source, "one-common-observation", "artificial-native-not-AUTH",
            a.geometry.binding(), opportunity_, opportunity_, witness.state().s, *a.epsilon, witness.cap()}};
        NoExtensions guard;
        auto prepared = position_->prepare_position(c, {opportunity_, tag(), "blocker-observed", ""}, guard);
        check(position_->view().same_identity(before), "prepared certificate released ownership early");
        position_->commit(std::move(prepared));
        observed_lower_ = witness.state().s;
        check(same(position_->view().structure().actions.at("blocker")->input->q, observed_lower_),
              "committed progress differs from exact controller certificate");
        check(position_->view().current_snapshot("blocker").mask() ==
              blocker_.n_mask(observed_lower_, blocker_.length()).mask(),
              "committed retirement differs from direct residual geometry");
        const auto endpoint = blocker_.n_mask(blocker_.length(), blocker_.length());
        for (const auto& cell : endpoint.mask())
            check(position_->view().structure().owners.at(cell).action == "blocker",
                  "query removed blocker endpoint responsibility");
        ++observations_;
        std::cout << "{\"event\":\"actual_position_committed\",\"at\":"; interval(opportunity_);
        std::cout << ",\"lower\":"; interval(observed_lower_);
        std::cout << ",\"endpoint_retained\":true}\n";
    }
    void publish_native_end(const R& at) {
        const auto witness = blocker_motion_.snapshot();
        check(deliver_end_ && !end_delivered_ && actual_end_ && witness.closed() &&
              same(witness.state().s, blocker_.length()) && same(witness.state().v, rat(0)) &&
              same(at, O::add(*actual_end_, rat(1, 4))), "END lacks real closed witness or delivery lag");
        now_ = at;
        auto end = delta();
        end.structure.actions.emplace("blocker", nullptr);
        const auto view = position_->view();
        for (const auto& item : view.structure().owners)
            if (item.second.action == "blocker") end.structure.owners.emplace(item.first, nullptr);
        const auto endpoint = blocker_.n_mask(blocker_.length(), blocker_.length());
        for (const auto& cell : endpoint.mask()) {
            const auto found = view.structure().owners.find(cell);
            check(found != view.structure().owners.end() && found->second.action == "blocker",
                  "native END tried to overwrite foreign terminal owner");
            end.structure.owners[cell] = std::make_shared<const I::Owner>(
                I::Owner{"blocker-resident", "blocker-agent", "", false});
        }
        commit(end);
        end_delivered_ = true;
        for (const auto& cell : endpoint.mask()) {
            const auto& owner = position_->view().structure().owners.at(cell);
            check(owner.agent == "blocker-agent" && owner.action.empty() && !owner.geometric,
                  "native END lost blocker endpoint residence");
        }
        std::cout << "{\"event\":\"blocker_native_END_delivered\",\"ended_at\":";
        interval(*actual_end_); std::cout << ",\"received_at\":"; interval(at);
        std::cout << ",\"terminal_resident_retained\":true,\"production_AUTH\":false}\n";
    }
    void advance_blocker(const R& target) {
        while (!blocker_motion_.snapshot().closed()) {
            const auto snap = blocker_motion_.snapshot();
            const R boundary = O::add(snap.segment_start(), snap.segment().duration());
            if (O::cmp(boundary, target) > 0) break;
            blocker_motion_.advance_to(boundary);
            if (blocker_motion_.snapshot().closed()) actual_end_.reset(new R(boundary));
        }
        blocker_motion_.advance_to(target);
    }
    void advance(const R& target) {
        check(O::cmp(target, now_) >= 0, "world time moved backwards");
        if (observations_ == 0 && O::cmp(target, opportunity_) >= 0) observe();
        advance_blocker(target);
        if (deliver_end_ && !end_delivered_ && actual_end_) {
            const R receipt = O::add(*actual_end_, rat(1, 4));
            if (O::cmp(receipt, target) <= 0) publish_native_end(receipt);
        }
        now_ = target;
        // Later private true progress may NOT replace the only committed sample.
        check(end_delivered_ || same(position_->view().structure().actions.at("blocker")->input->q,
                   observations_ ? observed_lower_ : rat(0)),
              "unobserved motion leaked into committed progress");
    }
public:
    TaskWorld(const R& error, const G& first, const Opportunity& opportunity, Authorization authorization,
          const R& requester_eta, bool deliver_end)
        : blocker_(geometry("blocker", {rat(2), rat(3, 2)}, {rat(8), rat(3, 2)}, error)), deliver_end_(deliver_end),
          blocker_motion_({rat(1), rat(2), rat(6), rat(1)}, blocker_.length(), rat(0),
                          rat(0), rat(-1), "blocker"), opportunity_(opportunity.at),
          opportunity_name_(opportunity.name), authorization_(authorization), requester_eta_(requester_eta) {
        check(O::cmp(requester_eta_, rat(-1)) >= 0 && O::cmp(requester_eta_, rat(1)) <= 0,
              "requester eta outside the unchanged delta=1 domain");
        S seed("empty", rat(0));
        S::Delta residents{{"empty", "residents", {}, {}, {}}, rat(0), {}, {}};
        const auto b = blocker_.n_mask(rat(0), rat(0));
        const auto r = first.n_mask(rat(0), rat(0));
        for (const auto& cell : b.mask())
            check(residents.structure.owners.emplace(cell, std::make_shared<const I::Owner>(
                I::Owner{"blocker-resident", "blocker-agent", "", false})).second, "duplicate blocker start");
        for (const auto& cell : r.mask())
            check(residents.structure.owners.emplace(cell, std::make_shared<const I::Owner>(
                I::Owner{"requester-resident", "requester", "", false})).second, "initial robots overlap");
        auto prepared = seed.prepare(residents); seed.commit(std::move(prepared));
        position_.reset(new P(seed, {}));
        auto grant = delta();
        grant.structure.actions.emplace("blocker", action(blocker_, "blocker-agent"));
        const auto full = blocker_.n_mask(rat(0), blocker_.length());
        for (const auto& cell : full.mask()) {
            const auto& owners = position_->view().structure().owners;
            const auto found = owners.find(cell);
            check(found == owners.end() || found->second.agent == "blocker-agent", "blocker full cap hits waiting start");
            grant.structure.owners.emplace(cell, std::make_shared<const I::Owner>(
                I::Owner{"blocker", "blocker-agent", "blocker", true}));
        }
        commit(grant, {{"blocker", {"blocker-seed", "blocker-current", "", ""}}});
        check(blocker_motion_.install_cap(rat(0), blocker_.length()),
              "blocker failed to install the already committed full grant");
        check(blocker_motion_.run(rat(0)), "blocker public native RUN did not start");
    }
    P::View public_view() const { return position_->view(); }
    bool edge(const G& g) {
        const std::string move = g.binding().move_occurrence;
        resident(g);
        const auto desired = g.n_mask(rat(0), g.length());
        auto request = delta();
        request.structure.demands.emplace(move, std::make_shared<const I::Demand>(
            I::Demand{"requester", "", desired.mask(), now_, true}));
        commit(request);
        if (!attempt(move)) {
            const auto frozen = position_->view();
            const auto& relations = frozen.structure().demands.at(move)->relations;
            check(relations.size() == 1 && relations.front().action == "blocker" &&
                  relations.front().retirable && relations.front().threshold,
                  "unexpected or nonretirable route blocker");
            const R threshold = *relations.front().threshold;
            std::vector<std::string> overlap;
            for (const auto& cell : desired.mask()) {
                const auto found = frozen.structure().owners.find(cell);
                if (found != frozen.structure().owners.end() && found->second.action == "blocker") overlap.push_back(cell);
            }
            const auto& active = *frozen.structure().actions.at("blocker")->input;
            const auto extracted = pie_query_geometry::extract<O>(active.geometry, active.q, active.b, overlap);
            check(same(threshold, extracted.physical_exit), "Index/Geometry continuation threshold mismatch");
            std::cout << "{\"event\":\"waiting\",\"opportunity\":\"" << opportunity_name_
                      << "\",\"move\":\"" << move << "\",\"owner\":\"" << relations.front().owner
                      << "\",\"threshold\":\"" << rational_text(threshold) << "\",\"at\":";
            interval(now_); std::cout << "}\n";
            if (observations_ == 0) {
                check(O::cmp(now_, opportunity_) < 0, "missed the common observation opportunity");
                waiting_ = O::add(waiting_, O::sub(opportunity_, now_));
                advance(opportunity_);
            }
            resident(g);
            bool released = attempt(move);
            check(released == (O::cmp(observed_lower_, threshold) > 0),
                  "actual PositionCommit retirement violates strict threshold");
            if (!released && deliver_end_ && !end_delivered_) {
                const R wait_start = now_;
                while (!blocker_motion_.snapshot().closed()) {
                    const auto snap = blocker_motion_.snapshot();
                    advance(O::add(snap.segment_start(), snap.segment().duration()));
                }
                check(bool(actual_end_), "closed blocker lacks actual boundary timestamp");
                advance(O::add(*actual_end_, rat(1, 4)));
                waiting_ = O::add(waiting_, O::sub(now_, wait_start));
                resident(g);
                released = attempt(move);
            }
            if (!released) {
                const auto after = position_->view();
                const auto& still = after.structure().demands.at(move)->relations;
                check(observations_ == 1 && still.size() == 1 && still.front().owner == "blocker" &&
                      same(*still.front().threshold, threshold) && !after.structure().actions.count(move),
                      "insufficient evidence lost pending demand or installed an unauthorized MOVE");
                // Finite censoring point: preserve the resident and pending demand.
                // No new observation, END, cap grant, or later true progress is invented.
                std::cout << "{\"event\":\"blocked_after_only_observation\",\"opportunity\":\""
                          << opportunity_name_ << "\",\"move\":\"" << move
                          << "\",\"threshold\":\"" << rational_text(threshold)
                          << "\",\"resident_retained\":true,\"observed_lower\":";
                interval(observed_lower_); std::cout << "}\n";
                return false;
            }
        }
        auto grant = delta();
        grant.structure.demands.emplace(move, nullptr);
        grant.structure.actions.emplace(move, action(g, "requester"));
        for (const auto& cell : desired.mask()) {
            const auto& owners = position_->view().structure().owners;
            const auto found = owners.find(cell);
            check(found == owners.end() || found->second.agent == "requester", "full MOVE admission hits foreign owner");
            grant.structure.owners.emplace(cell, std::make_shared<const I::Owner>(
                I::Owner{move, "requester", move, true}));
        }
        commit(grant, {{move, {move + "-seed", move + "-current", "", ""}}});
        // Real cumulative-cap installation follows the center's committed grant.
        const R entered_at = now_;
        Controller c({rat(1), rat(2), rat(6), rat(1)}, g.length(), now_,
                     rat(0), requester_eta_, move);
        check(same(position_->view().structure().actions.at(move)->input->b, g.length()) &&
              same(c.snapshot().cap(), rat(0)), "cap installed before committed grant");
        check(c.install_cap(now_, g.length()), "initial cumulative cap failed to install");
        ++cap_grants_;
        check(same(c.snapshot().state().s, rat(0)) && same(c.snapshot().state().v, rat(0)),
              "cap installation moved the reference state");
        check(c.run(now_), "native RUN failed after committed full-cap grant");
        ++run_commands_;
        std::cout << "{\"event\":\"requester_full_cap_installed\",\"move\":\""
                  << move << "\",\"at\":"; interval(now_);
        std::cout << ",\"from\":\"0\",\"to\":\"" << rational_text(g.length())
                  << "\",\"original_move_unchanged\":true}\n";
        while (!c.snapshot().closed()) {
            const auto before = c.snapshot();
            const R boundary = O::add(before.segment_start(), before.segment().duration());
            advance(boundary);
            c.advance_to(boundary);
            check(c.snapshot().move_id() == move && same(c.snapshot().length(), g.length()) &&
                  same(c.snapshot().cap(), g.length()) && same(c.snapshot().eta(), requester_eta_),
                  "edge changed original MOVE, installed cap or the fixed private eta");
        }
        check(same(c.snapshot().state().s, g.length()) && same(c.snapshot().state().v, rat(0)),
              "native END lacks a reached original endpoint at rest");
        // Explicit native lifecycle premise: exact closed same-MOVE witness
        // authorizes END; production END/authentication are not implemented.
        auto end = delta();
        end.structure.actions.emplace(move, nullptr);
        for (const auto& cell : desired.mask()) {
            check(position_->view().structure().owners.at(cell).action == move, "END attempted foreign owner deletion");
            end.structure.owners.emplace(cell, nullptr);
        }
        const auto endpoint = g.n_mask(g.length(), g.length());
        for (const auto& cell : endpoint.mask())
            end.structure.owners[cell] = std::make_shared<const I::Owner>(
                I::Owner{"requester-resident", "requester", "", false});
        commit(end);
        for (const auto& cell : endpoint.mask())
            check(position_->view().structure().owners.at(cell).agent == "requester" &&
                  position_->view().structure().owners.at(cell).action.empty(), "END lost endpoint resident");
        ++edges_;
        const R duration = O::sub(now_, entered_at);
        move_durations_.push_back(duration);
        moving_ = O::add(moving_, duration);
        std::cout << "{\"event\":\"original_move_end\",\"move\":\"" << move
                  << "\",\"at\":"; interval(now_);
        std::cout << ",\"endpoint_resident_retained\":true}\n";
        return true;
    }
    void hold_censored_until(const R& horizon) {
        check(O::cmp(now_, horizon) <= 0 && position_->view().structure().demands.size() == 1,
              "censoring needs a live pending demand before the fixed horizon");
        waiting_ = O::add(waiting_, O::sub(horizon, now_));
        advance(horizon);
        const auto view = position_->view();
        check(view.structure().demands.size() == 1 && !ready(view.structure().demands.begin()->first),
              "censored demand became ready without resuming execution");
    }
    bool end_delivered() const { return end_delivered_; }
    Result result(bool complete) const {
        return {now_, waiting_, observed_lower_, observations_, edges_, grant_attempts_,
                cap_grants_, run_commands_, prefix_no_group_checks_, complete, moving_, move_durations_};
    }
};

} // namespace
