#ifndef PIE_LEARNING_COMPONENT_SNAPSHOT_HPP
#define PIE_LEARNING_COMPONENT_SNAPSHOT_HPP

// Synthetic component fixture export only. The isolated header copies add
// const accessors; this header neither authenticates nor publishes a root.
#include "pie_position_commit.hpp"
#include "pie_geometry_flint.hpp"
#include <limits>
#include <ostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>

namespace pie_learning_component {
using Ops = pie_geometry::FlintOps;
using Real = Ops::Real;
using Position = pie_position_commit::PositionCommit<Ops>;
using Scheduler = Position::Scheduler;
using Index = Position::Structure;

inline void json_string(std::ostream& out, const std::string& value) {
    static const char hex[] = "0123456789abcdef";
    out << '"';
    for (const unsigned char byte : value) {
        if (byte == '"') out << "\\\"";
        else if (byte == '\\') out << "\\\\";
        else if (byte < 0x20)
            out << "\\u00" << hex[byte >> 4] << hex[byte & 15];
        else out.put(static_cast<char>(byte));
    }
    out << '"';
}

namespace detail {
struct Rational {
    fmpq_t value;
    Rational() { fmpq_init(value); }
    ~Rational() { fmpq_clear(value); }
    Rational(const Rational&) = delete;
    Rational& operator=(const Rational&) = delete;
};
struct Decimal {
    char* value;
    explicit Decimal(const fmpz* integer) : value(fmpz_get_str(nullptr, 10, integer)) {
        if (!value) throw std::runtime_error("exact integer formatting failed");
    }
    ~Decimal() { flint_free(value); }
    Decimal(const Decimal&) = delete;
    Decimal& operator=(const Decimal&) = delete;
};
inline const char* policy_name(pie_query::QueryPolicy policy) {
    switch (policy) {
        case pie_query::QueryPolicy::Srdc: return "SRDC";
        case pie_query::QueryPolicy::RoundRobin: return "RoundRobin";
        case pie_query::QueryPolicy::BlockerCount: return "BlockerCount";
        case pie_query::QueryPolicy::SrdcWorkOnly: return "SrdcWorkOnly";
        case pie_query::QueryPolicy::SrdcWaitOnly: return "SrdcWaitOnly";
        case pie_query::QueryPolicy::SrdcUnitWeight: return "SrdcUnitWeight";
    }
    throw std::invalid_argument("unknown component policy");
}
inline const char* relation_name(pie_query::RelationKind kind) {
    switch (kind) {
        case pie_query::RelationKind::RetirableAtCurrentCap: return "RetirableAtCurrentCap";
        case pie_query::RelationKind::CapInsufficient: return "CapInsufficient";
        case pie_query::RelationKind::EndpointRetained: return "EndpointRetained";
        case pie_query::RelationKind::OtherRetainedResponsibility: return "OtherRetainedResponsibility";
        case pie_query::RelationKind::NonQueryOwner: return "NonQueryOwner";
    }
    throw std::invalid_argument("unknown relation reason");
}
inline void binding(std::ostream& out, const Scheduler::Binding& b) {
    out << "{\"geometry_version\":"; json_string(out, b.geometry_version);
    out << ",\"number_encoding\":"; json_string(out, b.number_encoding);
    out << ",\"coordinate_frame\":"; json_string(out, b.coordinate_frame);
    out << ",\"distance_unit\":"; json_string(out, b.distance_unit);
    out << ",\"move_occurrence\":"; json_string(out, b.move_occurrence);
    out << '}';
}
} // namespace detail

// Public helper also serializes the C++ reference result on stderr.
inline void exact_number(std::ostream& out, const Real& value) {
    if (!Ops::valid(value)) throw std::invalid_argument("invalid exact component number");
    detail::Rational rational;
    if (!Ops::copy_rational(value, rational.value)) {
        out << "{\"unsupported\":\"non_rational\"}";
        return;
    }
    fmpq_canonicalise(rational.value);
    detail::Decimal numerator(fmpq_numref(rational.value));
    detail::Decimal denominator(fmpq_denref(rational.value));
    out << "{\"numerator\":"; json_string(out, numerator.value);
    out << ",\"denominator\":"; json_string(out, denominator.value);
    out << '}';
}

inline std::size_t demand_weight(const Position::View& view, const Index::Demand& demand) {
    std::size_t downstream = 0;
    if (!demand.requester_action.empty()) {
        const auto found = view.structure().out.find(demand.requester_action);
        if (found != view.structure().out.end()) downstream = found->second;
    }
    if (downstream == (std::numeric_limits<std::size_t>::max)())
        throw std::overflow_error("component dependency weight overflow");
    return downstream + 1;
}

namespace detail {
inline void optional_number(std::ostream& out, const std::shared_ptr<const Real>& value) {
    if (value) exact_number(out, *value);
    else out << "null";
}
inline void evidence(std::ostream& out, const Scheduler::Evidence& e) {
    out << "{\"action\":"; json_string(out, e.action);
    out << ",\"source\":"; json_string(out, e.source);
    out << ",\"key\":"; json_string(out, e.key);
    out << ",\"provenance\":"; json_string(out, e.provenance);
    out << ",\"binding\":"; binding(out, e.binding);
    out << ",\"captured\":"; exact_number(out, e.captured);
    out << ",\"delivered\":"; exact_number(out, e.delivered);
    out << ",\"lower\":"; exact_number(out, e.lower);
    out << ",\"epsilon\":"; exact_number(out, e.epsilon);
    out << ",\"cap_at_capture\":"; exact_number(out, e.cap_at_capture);
    out << '}';
}
inline void receipt(std::ostream& out, const Scheduler::Receipt& r) {
    out << "{\"profile\":"; json_string(out, r.profile);
    out << ",\"source\":"; json_string(out, r.source);
    out << ",\"key\":"; json_string(out, r.key);
    out << ",\"provenance\":"; json_string(out, r.provenance);
    out << ",\"epsilon\":"; optional_number(out, r.epsilon);
    out << ",\"published\":"; exact_number(out, r.published);
    out << ",\"captured\":"; exact_number(out, r.captured);
    out << ",\"committed\":"; exact_number(out, r.committed);
    out << ",\"delivered\":"; exact_number(out, r.delivered);
    out << ",\"charged_work\":"; exact_number(out, r.charged_work);
    out << '}';
}
} // namespace detail

inline std::string snapshot_json(Position::View view, const Real& now,
                                 const std::string& run_id, const std::string& snapshot_id) {
    if (run_id.empty() || snapshot_id.empty() || !Ops::valid(now) ||
        Ops::cmp(now, view.export_committed_at()) < 0)
        throw std::invalid_argument("invalid component export identity or time");
    const auto& structure = view.structure();
    std::ostringstream out;
    out << "{\"schema\":\"pie_query_component_snapshot_v1\","
        << "\"source_kind\":\"synthetic_component_fixture\","
        << "\"outer_publication_verified\":false,\"run_id\":";
    json_string(out, run_id);
    out << ",\"snapshot_id\":"; json_string(out, snapshot_id);
    out << ",\"view_id\":"; json_string(out, structure.view_id);
    out << ",\"now\":"; exact_number(out, now);
    out << ",\"committed_at\":"; exact_number(out, view.export_committed_at());
    out << ",\"policy\":"; json_string(out, detail::policy_name(view.export_policy()));
    out << ",\"generation\":" << view.export_generation() << ",\"cursor\":";
    json_string(out, view.round_robin_cursor());
    out << ",\"actions\":[";
    bool comma = false;
    std::set<std::string, pie_query::KeyLess> profiles;
    for (const auto& item : structure.actions) {
        if (comma) out << ',';
        comma = true;
        const auto& a = *item.second->input;
        profiles.insert(a.profile);
        out << "{\"key\":"; json_string(out, item.first);
        out << ",\"agent\":"; json_string(out, a.agent);
        out << ",\"source\":"; json_string(out, a.source);
        out << ",\"profile\":"; json_string(out, a.profile);
        out << ",\"binding\":"; detail::binding(out, a.geometry.binding());
        out << ",\"q\":"; exact_number(out, a.q);
        out << ",\"cap\":"; exact_number(out, a.b);
        out << ",\"epsilon\":"; detail::optional_number(out, a.epsilon);
        out << ",\"eligible\":" << (a.eligible ? "true" : "false") << ",\"history\":[";
        const auto* history = view.export_history(item.first);
        bool separator = false;
        if (history) for (const auto& e : *history) {
            if (separator) out << ',';
            separator = true;
            detail::evidence(out, e);
        }
        out << "]}";
    }
    out << "],\"demands\":[";
    comma = false;
    for (const auto& item : structure.demands) {
        if (comma) out << ',';
        comma = true;
        const auto& d = *item.second->input;
        out << "{\"key\":"; json_string(out, item.first);
        out << ",\"agent\":"; json_string(out, d.agent);
        out << ",\"requester_action\":"; json_string(out, d.requester_action);
        out << ",\"weight\":" << demand_weight(view, d) << ",\"joined\":";
        exact_number(out, d.joined);
        out << ",\"other_ready\":" << (d.non_owner_eligible ? "true" : "false")
            << ",\"relations\":[";
        bool separator = false;
        for (const auto& relation : item.second->relations) {
            if (separator) out << ',';
            separator = true;
            out << "{\"owner\":"; json_string(out, relation.owner);
            out << ",\"action\":"; json_string(out, relation.action);
            out << ",\"retirable\":" << (relation.retirable ? "true" : "false")
                << ",\"kind\":";
            json_string(out, detail::relation_name(relation.kind));
            out << ",\"threshold\":"; detail::optional_number(out, relation.threshold);
            out << '}';
        }
        out << "]}";
    }
    out << "],\"receipts\":[";
    comma = false;
    for (const auto& profile : profiles) {
        const auto* r = view.export_receipt(profile);
        if (!r) continue;
        if (comma) out << ',';
        comma = true;
        detail::receipt(out, *r);
    }
    out << "]}";
    return out.str();
}
} // namespace pie_learning_component

#endif
