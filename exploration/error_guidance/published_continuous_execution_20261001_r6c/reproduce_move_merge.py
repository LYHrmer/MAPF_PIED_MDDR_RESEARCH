"""Run the exact controller updateQueue body at the consecutive MOVE seam.

This is a local semantic regression, not a replacement native simulation.
Pass an alternative successor controller path to compare its fix.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'source_snapshot/client/controllers/footbot_diffusion/footbot_diffusion.cpp'
source = SOURCE.read_text()
start = source.index('void CFootBotDiffusion::updateQueue() {')
end = source.index('\nvoid CFootBotDiffusion::ControlStep()', start)
body = source[start:end]
fixture = r'''
#include <deque>
#include <iostream>
#include <string>
using namespace std;
struct Action { enum Type { MOVE, TURN, STOP, STATION }; Type type; double x,y; deque<int> nodeIDS; };
struct CFootBotDiffusion { deque<Action> q; string robot_id="0", debug_id="disabled"; void updateQueue(); };
'''
fixture += body
fixture += r'''
int main() {
    CFootBotDiffusion controller;
    controller.q.push_back({Action::MOVE, 0.5, 0.0, {1}});
    controller.q.push_back({Action::MOVE, 1.0, 0.0, {2}});
    controller.updateQueue();
    bool intact = controller.q.size() == 2 && controller.q.front().nodeIDS == deque<int>{1}
        && controller.q.front().x == 0.5 && controller.q.back().nodeIDS == deque<int>{2};
    cout << "queue_size=" << controller.q.size() << "; front_node_count="
         << controller.q.front().nodeIDS.size() << "; first_target_x="
         << controller.q.front().x << "; strict_no_merge=" << intact << endl;
    return intact ? 0 : 1;
}
'''
with tempfile.TemporaryDirectory(prefix='r6_move_merge_') as temporary:
    directory = Path(temporary)
    cpp = directory / 'repro.cpp'
    binary = directory / 'repro'
    cpp.write_text(fixture)
    subprocess.run(['rtk', 'proxy', 'c++', '-std=c++17', '-O0', str(cpp), '-o', str(binary)], check=True)
    result = subprocess.run(['rtk', 'proxy', str(binary)], capture_output=True, text=True)
    print(json.dumps({'source': str(SOURCE), 'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(), 'exact_extracted_function_sha256': hashlib.sha256(body.encode()).hexdigest(), 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}, indent=2))
    raise SystemExit(result.returncode)
