"""Build pristine pinned ADDRESS out of tree; --help only, NO instance/search.

This is artifact preparation, not reproduction of the paper's experiments or a
fair fixed-initial-solution comparison. Never alters the author's checkout.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time

HERE = Path(__file__).resolve().parent
AUTHOR = 'b3d35c431ce03834f95e834d87986f2f341394a1'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def source_identity(root):
    def git(*args):
        return subprocess.check_output(['git', '--no-replace-objects', '-C', str(root), *args])
    if git('rev-parse', 'HEAD').decode().strip() != AUTHOR:
        raise ValueError('fixed author commit required')
    if git('status', '--porcelain', '--untracked-files=all').strip():
        raise ValueError('author checkout must be clean')
    pins = {}
    for entry in git('ls-tree', '-r', '-z', AUTHOR).split(b'\0'):
        if not entry:
            continue
        meta, name = entry.split(b'\t')
        mode, kind, oid = meta.decode().split()
        path = name.decode()
        if not (path.startswith(('src/', 'inc/')) or path in ('CMakeLists.txt', 'README.md', 'license.txt')):
            continue
        file = root/path
        if kind != 'blob' or mode not in ('100644', '100755') or file.is_symlink():
            raise ValueError('non-regular pinned source: '+path)
        raw = file.read_bytes()
        if raw != git('cat-file', 'blob', oid):
            raise ValueError('author bytes changed: '+path)
        pins[path] = {'blob_oid': oid, 'sha256': sha(raw), 'bytes': len(raw)}
    required = {'src/driver.cpp', 'src/LNS.cpp', 'inc/LNS.h', 'CMakeLists.txt', 'license.txt'}
    if not required <= set(pins):
        raise ValueError('incomplete source tree')
    # CMake GLOB also sees ignored, untracked source files. Reject those too.
    for pattern in ('src/*.cpp', 'src/CBS/*.cpp', 'src/PIBT/*.cpp', 'inc/**/*.h', 'inc/**/*.hpp'):
        for file in root.glob(pattern):
            if str(file.relative_to(root)) not in pins:
                raise ValueError('untracked compilation input: '+str(file))
    return pins


def build(root, output, adapter=False, extension=None):
    if extension == 'recovery':
        raise ValueError('legacy recovery requires its frozen commit; use budget_recovery for the shared deadline')
    if extension not in (None, 'loop_guard', 'budget_guard', 'budget_recovery') or (extension and not adapter):
        raise ValueError('extensions require the common-initial adapter')
    root, output = root.resolve(), output.resolve()
    if output == root or root in output.parents:
        raise ValueError('build must be outside author checkout')
    pins = source_identity(root)
    output.mkdir(parents=True, exist_ok=False)
    receipt = {'scope': 'PRISTINE_FULL_ADDRESS_COMPILE_AND_HELP_ONLY',
               'solver_instance_constructed': False, 'scientific_search_executed': False,
               'author_commit': AUTHOR, 'author_files': pins, 'stages': [],
               'script_sha256': sha(Path(__file__).read_bytes()), 'status': 'BUILDING'}
    compile_root = root
    if adapter:
        receipt['scope'] = 'ADDRESS_COMMON_INITIAL_ADAPTER_COMPILE_AND_HELP_ONLY'
        receipt['reward_semantics'] = 'AUTHOR_ATTEMPT_UPDATE_BEFORE_ROLLBACK_UNCHANGED'
        receipt['external_total_budget_integration'] = 'PENDING'
        if extension:
            receipt['scope'] = 'ADDRESS_COMMON_INITIAL_'+extension.upper()+'_COMPILE_AND_HELP_ONLY'
            receipt['extension'] = extension
    target = output/'build_receipt.json'

    def save():
        # Update only this newly created build's receipt, never another attempt.
        target.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')

    def stage(name, command, timeout, accepted=(0,)):
        started = time.monotonic_ns()
        logfile = output/(name+'.log')
        with logfile.open('xb') as stream:
            process = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT,
                                       start_new_session=True)
            timed_out = False
            try:
                code = process.wait(timeout=timeout)
            except BaseException as error:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
                timed_out = isinstance(error, subprocess.TimeoutExpired)
                receipt['stages'].append({'name': name, 'command': command,
                    'exit_code': process.returncode, 'timeout': timed_out,
                    'wall_ns': time.monotonic_ns()-started, 'log_sha256': sha(logfile.read_bytes()),
                    'error': type(error).__name__+': '+str(error)})
                save()
                raise
        receipt['stages'].append({'name': name, 'command': command, 'exit_code': code,
                                  'timeout': timed_out, 'wall_ns': time.monotonic_ns()-started,
                                  'log_sha256': sha(logfile.read_bytes())})
        save()
        if code not in accepted:
            raise RuntimeError(name+' failed; retained '+str(logfile))
        return logfile.read_bytes()

    save()
    try:
        if adapter:
            from address_adapter import materialize
            compile_root = output/'source_overlay'
            receipt['adapter_script_sha256'] = sha((HERE/'address_adapter.py').read_bytes())
            receipt['adapter_sources'] = materialize(root, compile_root, pins)
            if extension:
                import importlib
                modules = ['address_loop_guard']
                if extension in ('budget_guard', 'budget_recovery'):
                    modules.append('address_budget')
                if extension == 'budget_recovery':
                    modules.append('address_recovery')
                receipt['extension_order'] = modules
                receipt['extension_sources'] = {}
                receipt['extension_script_sha256'] = {}
                for name in modules:
                    module = importlib.import_module(name)
                    files = {str(p.relative_to(compile_root)): p.read_bytes()
                             for p in compile_root.rglob('*') if p.is_file()}
                    changed = module.adapt(files)
                    for relative, raw in changed.items():
                        part = Path(relative)
                        if part.is_absolute() or '..' in part.parts:
                            raise ValueError('extension path escape')
                        target_file = compile_root/part
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        target_file.write_bytes(raw)
                    receipt['extension_script_sha256'][name] = sha((HERE/(name+'.py')).read_bytes())
                    receipt['extension_sources'][name] = {
                        path: {'sha256': sha(raw), 'bytes': len(raw)} for path, raw in changed.items()}
            save()
        compiler = Path(shutil.which('g++') or '').resolve()
        cmake = Path(shutil.which('cmake') or '').resolve()
        if not compiler.is_file() or not cmake.is_file():
            raise RuntimeError('compiler/cmake unavailable')
        receipt.update({'compiler_sha256': sha(compiler.read_bytes()),
            'compiler_version': subprocess.check_output([str(compiler), '--version']).decode().splitlines()[0],
            'cmake_version': subprocess.check_output([str(cmake), '--version']).decode().splitlines()[0],
            'packages': subprocess.check_output(['dpkg-query', '-W', '-f=${Package} ${Version}\n',
                'libboost-dev', 'libboost-program-options-dev', 'libboost-system-dev',
                'libboost-filesystem-dev', 'libeigen3-dev']).decode().splitlines(),
            'environment_note': 'Host build evidence; author README requests Boost 1.81, installed version recorded, not a portable lock or paper environment match.'})
        save()
        stage('configure', [str(cmake), '-S', str(compile_root), '-B', str(output/'build'),
                           '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_CXX_COMPILER='+str(compiler)], 30)
        stage('compile', [str(cmake), '--build', str(output/'build'), '--parallel', '2'], 240)
        binary = output/'build/address'
        # driver.cpp handles help BEFORE po::notify, Instance and LNS construction.
        help_raw = stage('help', [str(binary), '--help'], 5, accepted=(1,))
        if b'--maxIterations' not in help_raw or b'--destroyStrategy' not in help_raw:
            raise ValueError('unexpected full-author help entry')
        if adapter and not all(flag in help_raw for flag in (b'--initialPaths', b'--adapterReceipt', b'--finalReserve')):
            raise ValueError('adapter help contract missing')
        if extension in ('budget_guard', 'budget_recovery') and not all(
                flag in help_raw for flag in (b'--cpuLimit', b'--cpuReserve', b'--attemptTrace', b'--phaseProfile')):
            raise ValueError('shared CPU budget help contract missing')
        if extension == 'budget_recovery' and not all(
                flag in help_raw for flag in (b'--recoveryPolicy', b'--recoveryTrace')):
            raise ValueError('recovery diagnostic help contract missing')
        if source_identity(root) != pins:
            raise ValueError('author source changed during build')
        receipt.update({'binary_sha256': sha(binary.read_bytes()), 'binary_bytes': binary.stat().st_size,
                        'status': 'COMPILED_HELP_ONLY', 'author_unchanged': True})
        save()
    except BaseException as error:
        receipt.update({'status': 'FAILED', 'error': type(error).__name__+': '+str(error)})
        save()
        raise
    return {'receipt': str(target), 'binary_sha256': receipt['binary_sha256'],
            'scope': receipt['scope'], 'status': receipt['status']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--author-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--adapter', action='store_true', help='compile project-owned common-initial overlay')
    parser.add_argument('--extension', choices=('loop_guard', 'budget_guard', 'budget_recovery'),
                        help='shared deadline precedes optional recovery; legacy recovery uses its frozen commit')
    args = parser.parse_args()
    print(json.dumps(build(args.author_root, args.output, args.adapter, args.extension), sort_keys=True))
