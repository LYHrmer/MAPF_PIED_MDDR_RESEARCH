// Project adapter to the unmodified ADDRESS SIPP at the pinned commit.
// No LNS neighborhood selection, bandit feedback, or replacement path search.
#include "SIPP.h"
#include <nlohmann/json.hpp>
#include <memory>
#include <sstream>
#include <stdexcept>

using json = nlohmann::json;
static const char* upstream = "b3d35c431ce03834f95e834d87986f2f341394a1";

int integer(const json& x, int upper = MAX_TIMESTEP) {
    if (!x.is_number_integer() || x.is_boolean()) throw std::runtime_error("integer required");
    auto n = x.get<long long>();
    if (n < 0 || n >= upper) throw std::runtime_error("integer outside declared domain");
    return static_cast<int>(n);
}

int main(int argc, char** argv) {
    if (argc == 2 && std::string(argv[1]) == "--describe") {
        std::cout << json({{"protocol", "address_sipp_bridge_v1"}, {"author_commit", upstream},
            {"scope", "AUTHOR_SIPP_FIXED_ORDER_PP_ADAPTER_NOT_FULL_ADDRESS"},
            {"solver_called", false}}).dump() << std::endl;
        return 0;
    }
    if (argc != 2 || std::string(argv[1]) != "--serve") return 2;
    std::unique_ptr<Instance> instance;
    std::vector<std::unique_ptr<SIPP>> solvers;
    std::string line;
    while (std::getline(std::cin, line)) {
        json answer = {{"author_commit", upstream}, {"status", "FAILED"}};
        try {
            const json request = json::parse(line);
            answer["seq"] = integer(request.at("seq"));
            const auto op = request.at("op").get<std::string>();
            if (op == "init") {
                if (instance) throw std::runtime_error("already initialized");
                const auto map = request.at("map_file").get<std::string>();
                const auto agents = request.at("agents_file").get<std::string>();
                // Parent writes and validates exact custom-format files. Never allow
                // the author's missing-file fallback to generate random instances.
                if (!std::ifstream(map).good() || !std::ifstream(agents).good())
                    throw std::runtime_error("missing declared input files");
                std::srand(integer(request.at("seed")));
                instance.reset(new Instance(map, agents));
                json lower = json::array();
                for (int a = 0; a < instance->getDefaultNumberOfAgents(); ++a) {
                    solvers.emplace_back(new SIPP(*instance, a));
                    lower.push_back(solvers.back()->my_heuristic[solvers.back()->start_location]);
                }
                answer.update({{"status", "READY"}, {"lower_bounds", lower},
                    {"base_length_max", MAX_TIMESTEP}, {"cache", "ONE_AUTHOR_HEURISTIC_TABLE_PER_AGENT"}});
            } else if (op == "search") {
                if (!instance) throw std::runtime_error("init required");
                const int a = integer(request.at("agent"), static_cast<int>(solvers.size()));
                PathTable table(instance->map_size);
                std::set<int> seen;
                for (const auto& row : request.at("fixed_paths")) {
                    const int id = integer(row.at("agent"), static_cast<int>(solvers.size()));
                    if (id == a || !seen.insert(id).second) throw std::runtime_error("invalid fixed robot");
                    Path path;
                    for (const auto& loc : row.at("path"))
                        path.emplace_back(integer(loc, instance->map_size));
                    if (path.empty()) throw std::runtime_error("empty fixed path");
                    table.insertPath(id, path);
                }
                ConstraintTable ct(instance->num_of_cols, instance->map_size, &table);
                const bool capped = !request.at("max_cost").is_null();
                if (capped) ct.length_max = integer(request.at("max_cost"));
                std::srand(integer(request.at("seed")));
                Path path = solvers[a]->findPath(ct); // original author implementation
                json vertices = json::array();
                for (const auto& entry : path) vertices.push_back(entry.location);
                answer.update({{"status", path.empty() ? (capped ? "EMPTY_CAPPED" : "EMPTY_BASE_LIMIT") : "FOUND"},
                    {"path", vertices}, {"num_expanded", solvers[a]->getNumExpanded()},
                    {"num_collisions", solvers[a]->num_collisions}, {"effective_max_cost", ct.length_max}});
            } else throw std::runtime_error("unsupported operation");
        } catch (const std::exception& error) {
            answer["reason"] = error.what();
        }
        std::cout << answer.dump() << std::endl;
    }
    return 0;
}
