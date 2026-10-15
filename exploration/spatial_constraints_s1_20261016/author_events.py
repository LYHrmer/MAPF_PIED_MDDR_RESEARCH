"""AGPL-3.0-or-later. Project adaptation using the unmodified SADG event API.

This is not the author's spatial-release algorithm or optimizer. Virtual event
vertices encode a separately verified CLEAR certificate; physical action status
does not become COMPLETED at CLEAR. Full SADG/ROS/world results are not implied.
"""
import hashlib
import importlib
import json
from pathlib import Path
import sys

AUTHOR_COMMIT = 'c2626d996121a9d6c128844a167b917db24418ac'


def load_author(checkout, receipt):
    checkout, receipt = Path(checkout).resolve(), Path(receipt)
    provenance = json.loads(receipt.read_text())
    if provenance['commit'] != AUTHOR_COMMIT or provenance['license'] != 'AGPL-3.0':
        raise ValueError('R16 author identity mismatch')
    modules = ('mapf.plan_tuple', 'sadg.vertex', 'sadg.dependency', 'sadg.status', 'sadg.location')
    prefix = 'sadg_controller/sadg_controller/'
    # Check all package initializers too, before executing any imported module.
    names = [prefix+x.replace('.', '/')+'.py' for x in modules]
    names += [prefix+x+'__init__.py' for x in ('', 'mapf/', 'sadg/')]
    for name in names:
        if hashlib.sha256((checkout/name).read_bytes()).hexdigest() != provenance['source_files'][name]:
            raise ValueError('author source changed: '+name)
    sys.path.insert(0, str(checkout/'sadg_controller'))
    loaded = {x: importlib.import_module('sadg_controller.'+x) for x in modules}
    for name, module in loaded.items():
        if Path(module.__file__).resolve() != checkout/prefix/(name.replace('.', '/')+'.py'):
            raise ValueError('unexpected imported author module')
    return loaded


class FixedOrderEvents:
    def __init__(self, author):
        self.Status = author['sadg.status'].Status
        Vertex, PlanTuple = author['sadg.vertex'].Vertex, author['mapf.plan_tuple'].PlanTuple
        Dependency = author['sadg.dependency'].Dependency
        # Zero-length vertices are logical certificates, never physical stop points.
        self.clear = Vertex('A_certificate', PlanTuple(0, 0, 0), 0)
        self.a_motion = Vertex('A_motion', [PlanTuple(-1, 0, 0), PlanTuple(2, 0, 0)], 0,
                               self.Status.IN_PROGRESS)
        self.b_motion = Vertex('B_motion', [PlanTuple(0, -1, 0), PlanTuple(0, 1, 0)], 0)
        self.b_motion.add_dependency(Dependency(self.clear, self.b_motion))

    def apply_certificate(self, certificate):
        if (certificate.get('accepted') is True
                and certificate.get('coverage') == 'ALL_ALLOWED_SUFFIX_AND_PERMANENT_HOLD'):
            self.clear.set_status(self.Status.COMPLETED)
        return self.b_motion.can_execute()
