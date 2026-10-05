"""Lossless, portable content-addressed evidence; no experiment dependencies."""
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path
import tempfile


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


class EvidenceStore:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, value):
        raw = canonical(value)
        key = hashlib.sha256(raw).hexdigest()
        relative = Path("objects") / key[:2] / (key + ".json.gz")
        path = self.root / relative
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            compressed = gzip.compress(raw, mtime=0)
            fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=key + ".tmp.")
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(compressed)
                os.replace(temporary, path)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        else:
            if hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest() != key:
                raise ValueError("corrupt immutable evidence object: " + str(path))
        return dict(schema="r19-cas-ref-v1", sha256=key, path=str(relative), raw_bytes=len(raw))

    def get(self, ref):
        path = self.root / ref["path"]
        expected = Path("objects") / ref["sha256"][:2] / (ref["sha256"] + ".json.gz")
        if Path(ref["path"]) != expected:
            raise ValueError("CAS path/hash mismatch")
        raw = gzip.decompress(path.read_bytes())
        if hashlib.sha256(raw).hexdigest() != ref["sha256"]:
            raise ValueError("CAS object hash mismatch")
        return json.loads(raw)

    def put_graph(self, graph):
        static = dict(vertices=[], type1=graph["type1"], groups=[])
        vertex_state, group_state = [], []
        for vertex in graph["vertices"]:
            static["vertices"].append({k: v for k, v in vertex.items() if k not in ("status", "duration", "progress")})
            vertex_state.append([vertex[k] for k in ("status", "duration", "progress")])
        for group in graph["groups"]:
            static["groups"].append(dict(uid=group["uid"], dependencies=[
                dict(forward=d["forward"], reverse=d["reverse"]) for d in group["dependencies"]]))
            ds = []
            for dependency in group["dependencies"]:
                choices = [dependency["forward"], dependency["reverse"]]
                active = choices.index(dependency["active"]) if dependency["active"] in choices else dict(literal=dependency["active"])
                ds.append([dependency["b"], active])
            group_state.append([group["switchable"], group["within_horizon"], ds])
        value = dict(schema="r19-graph-split-v1", topology=self.put(static),
            vertex_state=self.put(vertex_state), group_state=self.put(group_state), full_sha256=digest(graph))
        return self.put(value)

    def get_graph(self, ref):
        value = self.get(ref)
        if value["schema"] != "r19-graph-split-v1":
            raise ValueError("unknown graph encoding")
        topology = self.get(value["topology"])
        vertices = self.get(value["vertex_state"])
        groups = self.get(value["group_state"])
        result = copy.deepcopy(topology)
        if len(vertices) != len(result["vertices"]) or len(groups) != len(result["groups"]):
            raise ValueError("graph state length mismatch")
        for vertex, state in zip(result["vertices"], vertices):
            vertex.update(zip(("status", "duration", "progress"), state))
        for group, state in zip(result["groups"], groups):
            group["switchable"], group["within_horizon"] = state[:2]
            if len(group["dependencies"]) != len(state[2]):
                raise ValueError("dependency state length mismatch")
            for dependency, (bit, active) in zip(group["dependencies"], state[2]):
                dependency["b"] = bit
                dependency["active"] = active["literal"] if isinstance(active, dict) else [dependency["forward"], dependency["reverse"]][active]
        if digest(result) != value["full_sha256"]:
            raise ValueError("reconstructed graph differs from original")
        return result


def expand_episode(result, store):
    """Audit bridge: reconstruct old-shaped graph/snapshot data without solving."""
    result = copy.deepcopy(result)
    result["initial_graph"] = store.get_graph(result.pop("initial_graph_ref"))
    for gate in result["gates"]:
        gate["public_snapshot"] = store.get(gate.pop("public_snapshot_ref"))
    return result
