/* Generated audit fixture. Extracted upstream portions: MIT.
MIT License

Copyright (c) 2025 anonymous

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

*/
#include "BasicLNS.h"
#include <iomanip>
#include <iostream>
enum destroy_heuristic { RANDOMAGENTS, RANDOMWALK, HOTSPOTS, DESTROY_COUNT };
class OriginalBinding : public BasicLNS {
public:
    OriginalBinding(const Instance& instance, const string& bandit_algorithm_name,
           int neighborhoodSizes, double alphaUCB, double initialEpsilon,
           double lambdaDecay, double decayWindow) : BasicLNS(instance, 1.0, 8, 0, bandit_algorithm_name, neighborhoodSizes, alphaUCB, initialEpsilon, lambdaDecay, decayWindow,DESTROY_COUNT) {
        const string destroy_name = "Adaptive";
        if (destroy_name == "Adaptive")
    {
        ALNS = true;
        heuristicBanditStats.destroy_weights.assign(DESTROY_COUNT, 1);
        heuristicBanditStats.destroy_weights_squared.assign(DESTROY_COUNT, 1);
        heuristicBanditStats.destroy_counts.assign(DESTROY_COUNT, 0);

        // Initialize recent_rewards for AlphaUCB and EpsilonGreedy
        heuristicBanditStats.recent_rewards.resize(DESTROY_COUNT);
        for (int i = 0; i < DESTROY_COUNT; ++i) {
            heuristicBanditStats.recent_rewards[i].resize(decayWindow);
        }
        decay_factor = 0;
        reaction_factor = 0;
        if(numberOfNeighborhoodSizeCandidates > 0)
        {
            for(int index = 0; index < DESTROY_COUNT; index++)
            {
                neighborhoodBanditStats.push_back(new BanditStats());
                neighborhoodBanditStats[index]->destroy_weights.assign(numberOfNeighborhoodSizeCandidates, 1);
                neighborhoodBanditStats[index]->destroy_weights_squared.assign(numberOfNeighborhoodSizeCandidates, 1);
                neighborhoodBanditStats[index]->destroy_counts.assign(numberOfNeighborhoodSizeCandidates, 0);
                
            }
        }
    }
    }

    string getSolverName() const override { return "SOFTWARE_FIXTURE_ONLY"; }
    void observe(int arm, double value, bool condition) {
        heuristicBanditStats.banditIndex = arm;
        updateDestroyWeights(&heuristicBanditStats, value, condition);
    }
    void choose_pair() { sampleDestroyHeuristicAndNeighborhoodSize(); }
    void choose_one() { sampleDestroyHeuristic(&heuristicBanditStats); }
    void set_clock(int n) { iterationCount = n; }
    void set_queues(vector<deque<double>> values) {
        heuristicBanditStats.recent_rewards = values;
    }
    void report(const string& name) const {
        const auto& q = heuristicBanditStats.recent_rewards[0];
        cout << setprecision(17) << "{\"case\":\"" << name
             << "\",\"arms_parameter\":" << numberOfDestroyHeuristics
             << ",\"alpha\":" << alphaUCB
             << ",\"initial_epsilon\":" << initialEpsilon
             << ",\"lambda\":" << lambdaDecay
             << ",\"window_parameter\":" << decayWindow
             << ",\"clock\":" << iterationCount
             << ",\"epsilon\":" << epsilonT
             << ",\"selected\":" << heuristicBanditStats.banditIndex
             << ",\"size_bandit_objects\":" << neighborhoodBanditStats.size()
             << ",\"child_reward_rows\":"
             << (neighborhoodBanditStats.empty() ? 0 : neighborhoodBanditStats[0]->recent_rewards.size())
             << ",\"child_weight_rows\":"
             << (neighborhoodBanditStats.empty() ? 0 : neighborhoodBanditStats[0]->destroy_weights.size())
             << ",\"q0\":[";
        for (size_t i = 0; i < q.size(); ++i) {
            if (i) cout << ',';
            cout << q[i];
        }
        cout << "]}" << endl;
    }

};
class CorrectedBindingOnly : public BasicLNS {
public:
    CorrectedBindingOnly(const Instance& instance, const string& bandit_algorithm_name,
           int neighborhoodSizes, double alphaUCB, double initialEpsilon,
           double lambdaDecay, double decayWindow) : BasicLNS(instance, 1.0, 8, 0, bandit_algorithm_name, neighborhoodSizes, DESTROY_COUNT, alphaUCB, initialEpsilon, lambdaDecay, decayWindow) {
        const string destroy_name = "Adaptive";
        if (destroy_name == "Adaptive")
    {
        ALNS = true;
        heuristicBanditStats.destroy_weights.assign(DESTROY_COUNT, 1);
        heuristicBanditStats.destroy_weights_squared.assign(DESTROY_COUNT, 1);
        heuristicBanditStats.destroy_counts.assign(DESTROY_COUNT, 0);

        // Initialize recent_rewards for AlphaUCB and EpsilonGreedy
        heuristicBanditStats.recent_rewards.resize(DESTROY_COUNT);
        for (int i = 0; i < DESTROY_COUNT; ++i) {
            heuristicBanditStats.recent_rewards[i].resize(decayWindow);
        }
        decay_factor = 0;
        reaction_factor = 0;
        if(numberOfNeighborhoodSizeCandidates > 0)
        {
            for(int index = 0; index < DESTROY_COUNT; index++)
            {
                neighborhoodBanditStats.push_back(new BanditStats());
                neighborhoodBanditStats[index]->destroy_weights.assign(numberOfNeighborhoodSizeCandidates, 1);
                neighborhoodBanditStats[index]->destroy_weights_squared.assign(numberOfNeighborhoodSizeCandidates, 1);
                neighborhoodBanditStats[index]->destroy_counts.assign(numberOfNeighborhoodSizeCandidates, 0);
                
            }
        }
    }
    }

    string getSolverName() const override { return "SOFTWARE_FIXTURE_ONLY"; }
    void observe(int arm, double value, bool condition) {
        heuristicBanditStats.banditIndex = arm;
        updateDestroyWeights(&heuristicBanditStats, value, condition);
    }
    void choose_pair() { sampleDestroyHeuristicAndNeighborhoodSize(); }
    void choose_one() { sampleDestroyHeuristic(&heuristicBanditStats); }
    void set_clock(int n) { iterationCount = n; }
    void set_queues(vector<deque<double>> values) {
        heuristicBanditStats.recent_rewards = values;
    }
    void report(const string& name) const {
        const auto& q = heuristicBanditStats.recent_rewards[0];
        cout << setprecision(17) << "{\"case\":\"" << name
             << "\",\"arms_parameter\":" << numberOfDestroyHeuristics
             << ",\"alpha\":" << alphaUCB
             << ",\"initial_epsilon\":" << initialEpsilon
             << ",\"lambda\":" << lambdaDecay
             << ",\"window_parameter\":" << decayWindow
             << ",\"clock\":" << iterationCount
             << ",\"epsilon\":" << epsilonT
             << ",\"selected\":" << heuristicBanditStats.banditIndex
             << ",\"size_bandit_objects\":" << neighborhoodBanditStats.size()
             << ",\"child_reward_rows\":"
             << (neighborhoodBanditStats.empty() ? 0 : neighborhoodBanditStats[0]->recent_rewards.size())
             << ",\"child_weight_rows\":"
             << (neighborhoodBanditStats.empty() ? 0 : neighborhoodBanditStats[0]->destroy_weights.size())
             << ",\"q0\":[";
        for (size_t i = 0; i < q.size(); ++i) {
            if (i) cout << ',';
            cout << q[i];
        }
        cout << "]}" << endl;
    }

};

int main(int argc, char**) {
    Instance instance;
    const string alpha = "AlphaUCB", epsilon = "EpsilonGreedy";
    if (argc > 1) {
        // Deliberately exercise the source's inconsistent child dimensions.
        // _GLIBCXX_ASSERTIONS must stop BEFORE an invalid vector access.
        CorrectedBindingOnly dimensions(instance, alpha, 5, 10000, .5, 10, 100);
        dimensions.report("corrected_binding_size5_before_selection");
        dimensions.choose_pair();
        return 0;
    }
    OriginalBinding original(instance, alpha, 5, 10000, .5, 10, 100);
    original.report("original_readme_binding");
    for (int i = 1; i <= 105; ++i) original.observe(0, i, true);
    original.report("original_after_105_positive_rewards");
    original.choose_pair();
    original.report("original_after_one_two_level_selection");

    CorrectedBindingOnly only_success(instance, alpha, 0, 2, .5, .01, 3);
    only_success.report("binding_corrected_prefill");
    only_success.observe(0, 6, true);
    only_success.report("first_positive_reward");
    only_success.observe(0, 0, false);
    only_success.observe(0, -4, false);
    only_success.report("zero_and_negative_not_admitted");
    only_success.observe(0, 3, true);
    only_success.report("second_positive_reward");
    for (int i = 0; i < 1000; ++i) only_success.observe(1, 1, true);
    only_success.report("other_arm_updates_do_not_age_q0");

    CorrectedBindingOnly selector(instance, alpha, 0, 2, .5, .01, 3);
    selector.set_queues({{0}, {.5, .5}, {-100}});
    selector.choose_one();
    selector.report("ucb_denominator_counterexample");

    CorrectedBindingOnly one_level(instance, alpha, 0, 2, .5, .01, 3);
    one_level.choose_pair();
    one_level.report("one_level_clock");
    CorrectedBindingOnly two_level(instance, alpha, 3, 2, .5, .01, 3);
    two_level.choose_pair();
    two_level.report("two_level_clock_safe_dimensions");

    CorrectedBindingOnly greedy(instance, epsilon, 0, 2, .5, .01, 3);
    greedy.set_clock(99);
    greedy.choose_one();
    greedy.report("epsilon_restart_at_100");
}
