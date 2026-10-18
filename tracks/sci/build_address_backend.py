"""Compile a pinned original SIPP adapter. No problem or search is executed."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

HERE = Path(__file__).resolve().parent
AUTHOR = 'b3d35c431ce03834f95e834d87986f2f341394a1'
SOURCES = ['src/SIPP.cpp', 'src/SingleAgentSolver.cpp', 'src/Instance.cpp',
           'src/ConstraintTable.cpp', 'src/PathTable.cpp', 'src/ReservationTable.cpp',
           'src/common.cpp']


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def source_identity(root):
    def git(*args):
        return subprocess.check_output(['git', '--no-replace-objects', '-C', str(root), *args])
    if git('rev-parse', 'HEAD').decode().strip() != AUTHOR:
        raise ValueError('author checkout must be at the fixed commit')
    pins = {}
    for record in git('ls-tree', '-r', '-z', AUTHOR).split(b'\0'):
        if not record:
            continue
        meta, name = record.split(b'\t')
        mode, kind, oid = meta.decode().split()
        path = name.decode()
        if path not in SOURCES and not (path.startswith('inc/') and path.endswith(('.h', '.hpp'))):
            continue
        file = root / path
        if kind != 'blob' or mode not in ('100644', '100755') or file.is_symlink():
            raise ValueError('regular author file required: ' + path)
        raw = file.read_bytes()
        expected = git('cat-file', 'blob', oid)
        if raw != expected:
            raise ValueError('author bytes changed: ' + path)
        pins[path] = {'blob_oid': oid, 'sha256': digest(raw), 'bytes': len(raw)}
    if not set(SOURCES) <= set(pins):
        raise ValueError('missing source closure')
    return pins


def build(author_root, output):
    author_root, output = author_root.resolve(), output.resolve()
    pins = source_identity(author_root)
    compiler = Path(shutil.which('g++') or '').resolve()
    if not compiler.is_file():
        raise ValueError('g++ unavailable')
    output.mkdir(parents=True, exist_ok=False)  # Never erase an earlier failed build.
    binary = output / 'address_sipp_bridge'
    cpp = HERE / 'address_sipp_bridge.cpp'
    command = [str(compiler), '-std=c++17', '-O2', '-DNDEBUG',
               '-I' + str(author_root / 'inc'), '-I' + str(author_root / 'inc/CBS'),
               str(cpp), *[str(author_root / p) for p in SOURCES], '-o', str(binary)]
    started = time.monotonic_ns()
    try:
        run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             timeout=120, check=False)
        log, exit_code, timed_out = run.stdout, run.returncode, False
    except subprocess.TimeoutExpired as error:
        log, exit_code, timed_out = error.stdout or b'', None, True
    (output / 'compile.log').write_bytes(log)
    receipt = {'scope': 'COMPILE_AND_DESCRIBE_ONLY_NO_INSTANCE_OR_SEARCH',
               'author_commit': AUTHOR, 'author_files': pins, 'command': command,
               'compiler_version': subprocess.check_output([str(compiler), '--version']).decode().splitlines()[0],
               'compiler_sha256': digest(compiler.read_bytes()), 'exit_code': exit_code,
               'compile_timeout': timed_out,
               'compile_wall_ns': time.monotonic_ns() - started,
               'bridge_sha256': digest(cpp.read_bytes()),
               'build_script_sha256': digest(Path(__file__).read_bytes()),
               'compile_log_sha256': digest(log)}
    # This is a host-specific build record, not a portable/container environment lock.
    receipt['header_packages'] = subprocess.check_output([
        'dpkg-query', '-W', '-f=${Package} ${Version}\n',
        'libboost-dev', 'nlohmann-json3-dev']).decode().splitlines()
    if exit_code == 0:
        try:
            if pins != source_identity(author_root):
                raise ValueError('author files changed during build')
            receipt['binary_sha256'] = digest(binary.read_bytes())
            receipt['describe'] = json.loads(subprocess.check_output([str(binary), '--describe'], timeout=5))
        except Exception as error:
            receipt['post_compile_error'] = type(error).__name__ + ': ' + str(error)
    (output / 'build_receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    if exit_code != 0 or 'post_compile_error' in receipt:
        raise RuntimeError('compile failed; retained ' + str(output / 'compile.log'))
    return {'binary': str(binary), 'sha256': receipt['binary_sha256'], 'scope': receipt['scope']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--author-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=HERE / '.native_build')
    args = parser.parse_args()
    print(json.dumps(build(args.author_root, args.output), sort_keys=True))
