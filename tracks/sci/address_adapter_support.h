// Project-owned adapter contract. No author solver code is copied here.
#pragma once
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <limits>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

namespace address_adapter {
using Paths = std::vector<std::vector<int>>;
using Clock = std::chrono::steady_clock;
struct State {
    Clock::time_point entry = Clock::now();
    double total_seconds = 0, final_reserve = 0;
    std::string initial_file, receipt_file;
    unsigned seed = 0;
    std::mt19937 seeds;
    bool initial_validated = false, final_validated = false;
    int initial_soc = -1, final_soc = -1;
    double initial_check_seconds = 0, final_check_seconds = 0;
};
inline State& state() { static State value; return value; }
inline unsigned next_seed() { return state().seeds(); }
inline double elapsed() { return std::chrono::duration<double>(Clock::now()-state().entry).count(); }
inline double remaining() { return state().total_seconds-elapsed(); }
inline int at(const std::vector<int>& p, size_t t) { return p[std::min(t, p.size()-1)]; }

// Full discrete MAPF check, including permanent terminal occupancy. Independently
// used at both import and final output; never restores individual paths.
inline int validate(const Paths& paths, int rows, int cols,
                    const std::vector<bool>& blocked, const std::vector<int>& starts,
                    const std::vector<int>& goals) {
    if (rows <= 0 || cols <= 0 || blocked.size() != size_t(rows)*cols || paths.empty()
        || paths.size() != starts.size() || paths.size() != goals.size())
        throw std::runtime_error("adapter: invalid shape");
    long long soc = 0;
    size_t horizon = 0;
    for (size_t a = 0; a < paths.size(); ++a) {
        const auto& p = paths[a];
        if (p.empty() || p.front() != starts[a] || p.back() != goals[a])
            throw std::runtime_error("adapter: endpoint mismatch");
        for (size_t t = 0; t < p.size(); ++t) {
            const int loc = p[t];
            if (loc < 0 || size_t(loc) >= blocked.size() || blocked[loc])
                throw std::runtime_error("adapter: invalid occupied cell");
            if (t && std::abs(loc/cols-p[t-1]/cols)+std::abs(loc%cols-p[t-1]%cols) > 1)
                throw std::runtime_error("adapter: invalid motion");
        }
        soc += p.size()-1;
        horizon = std::max(horizon, p.size());
    }
    if (soc > std::numeric_limits<int>::max()) throw std::runtime_error("adapter: SOC overflow");
    for (size_t t = 0; t < horizon; ++t)
        for (size_t a = 0; a < paths.size(); ++a)
            for (size_t b = a+1; b < paths.size(); ++b) {
                if (at(paths[a], t) == at(paths[b], t))
                    throw std::runtime_error("adapter: vertex or terminal collision");
                if (t && at(paths[a], t-1) == at(paths[b], t)
                    && at(paths[b], t-1) == at(paths[a], t))
                    throw std::runtime_error("adapter: opposing edge collision");
            }
    return int(soc);
}
inline Paths read_initial(size_t count) {
    std::ifstream input(state().initial_file);
    size_t n = 0;
    if (!(input >> n) || n != count) throw std::runtime_error("adapter: path count");
    Paths paths(n);
    for (auto& path : paths) {
        size_t length = 0;
        if (!(input >> length) || length == 0 || length > 1000000)
            throw std::runtime_error("adapter: path length");
        path.resize(length);
        for (auto& loc : path)
            if (!(input >> loc)) throw std::runtime_error("adapter: incomplete path");
    }
    std::string extra;
    if (input >> extra) throw std::runtime_error("adapter: trailing input");
    return paths;
}
template<class InstanceT>
inline int check(const Paths& paths, const InstanceT& instance) {
    std::vector<bool> blocked(instance.map_size);
    for (int i = 0; i < instance.map_size; ++i) blocked[i] = instance.isObstacle(i);
    return validate(paths, instance.num_of_rows, instance.num_of_cols, blocked,
                    instance.getStarts(), instance.getGoals());
}
template<class AgentsT, class InstanceT>
inline void check_final(const AgentsT& agents, const InstanceT& instance, int reported_soc) {
    const auto start = Clock::now();
    Paths paths;
    for (const auto& agent : agents) {
        paths.emplace_back();
        for (const auto& step : agent.path) paths.back().push_back(step.location);
    }
    state().final_soc = check(paths, instance);
    if (state().final_soc != reported_soc || state().final_soc > state().initial_soc)
        throw std::runtime_error("adapter: final SOC disagreement or worsening");
    state().final_check_seconds = std::chrono::duration<double>(Clock::now()-start).count();
    state().final_validated = true;
}
// This is an inner admission timer, not a replacement for process-group limits.
// The external controller must include launch, this output, reparse, and its
// independent final validation in the same total deadline.
inline int finish() {
    const bool ok = state().initial_validated && state().final_validated;
    const double before_receipt = elapsed();
    std::ofstream receipt(state().receipt_file);
    if (!receipt) throw std::runtime_error("adapter: receipt output failed");
    receipt << std::setprecision(17)
        << "{\"scope\":\"ADDRESS_COMMON_INITIAL_RECOMMENDED_CONFIG\","
        << "\"seed\":" << state().seed << ",\"initial_soc\":" << state().initial_soc
        << ",\"final_soc\":" << state().final_soc
        << ",\"inner_wall_before_receipt_s\":" << before_receipt
        << ",\"initial_check_s\":" << state().initial_check_seconds
        << ",\"final_check_s\":" << state().final_check_seconds
        << ",\"initial_and_final_validated\":" << (ok ? "true" : "false")
        << ",\"reward_semantics\":\"AUTHOR_ATTEMPT_UPDATE_BEFORE_ROLLBACK\","
        << "\"external_total_budget_verified\":false}\n";
    receipt.close();
    if (!receipt) throw std::runtime_error("adapter: receipt write failed");
    return ok && remaining() >= 0 ? 0 : 74;
}
} // namespace address_adapter
