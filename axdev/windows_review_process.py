"""Run untrusted acceptance code in a capability-free Windows AppContainer."""
from __future__ import annotations

import ctypes as c
from ctypes import wintypes as w
from contextlib import ExitStack, contextmanager
from functools import cache
import os
from pathlib import Path
import subprocess
import threading
import uuid

from .core import ContractError


class _Capabilities(c.Structure):
    _fields_ = [("sid", w.LPVOID), ("capabilities", w.LPVOID),
                ("count", w.DWORD), ("reserved", w.DWORD)]


class _Startup(c.Structure):
    _fields_ = [
        ("size", w.DWORD), ("reserved", w.LPWSTR), ("desktop", w.LPWSTR),
        ("title", w.LPWSTR), ("placement", w.DWORD * 8),
        ("show", w.WORD), ("reserved_size", w.WORD),
        ("reserved_data", w.LPVOID), ("stdin", w.HANDLE),
        ("stdout", w.HANDLE), ("stderr", w.HANDLE), ("attributes", w.LPVOID),
    ]


class _Process(c.Structure):
    _fields_ = [("process", w.HANDLE), ("thread", w.HANDLE),
                ("pid", w.DWORD), ("tid", w.DWORD)]


class _JobLimits(c.Structure):
    _fields_ = [("process_time", c.c_longlong), ("job_time", c.c_longlong),
                ("flags", w.DWORD), ("minimum_working_set", c.c_size_t),
                ("maximum_working_set", c.c_size_t), ("processes", w.DWORD),
                ("affinity", c.c_size_t), ("priority", w.DWORD),
                ("scheduling", w.DWORD), ("io", c.c_ulonglong * 6),
                ("process_memory", c.c_size_t), ("job_memory", c.c_size_t),
                ("peak_process_memory", c.c_size_t), ("peak_job_memory", c.c_size_t)]


def _check(ok, message):
    if not ok:
        raise ContractError(f"Windows reviewer {message} ({c.get_last_error()})")


@cache
def _native():
    if os.name != "nt":
        raise ContractError("Windows AppContainer reviewer requires Windows")

    def bind(dll, name, result, *args):
        function = getattr(dll, name)
        function.restype = result
        function.argtypes = args
        return function

    k32 = c.WinDLL("kernel32", use_last_error=True)
    userenv = c.WinDLL("userenv", use_last_error=True)
    advapi = c.WinDLL("advapi32", use_last_error=True)
    ptr, dword, handle, string = w.LPVOID, w.DWORD, w.HANDLE, w.LPWSTR
    native = {
        "system_dir": bind(k32, "GetSystemDirectoryW", w.UINT, string, w.UINT),
        "create_profile": bind(userenv, "CreateAppContainerProfile", c.c_long,
                               string, string, string, ptr, dword, c.POINTER(ptr)),
        "delete_profile": bind(userenv, "DeleteAppContainerProfile", c.c_long, string),
        "sid_text": bind(advapi, "ConvertSidToStringSidW", w.BOOL, ptr, c.POINTER(string)),
        "free_sid": bind(advapi, "FreeSid", ptr, ptr),
        "free": bind(k32, "LocalFree", ptr, ptr),
        "init_attrs": bind(k32, "InitializeProcThreadAttributeList", w.BOOL,
                           ptr, dword, dword, c.POINTER(c.c_size_t)),
        "set_attr": bind(k32, "UpdateProcThreadAttribute", w.BOOL,
                         ptr, dword, c.c_size_t, ptr, c.c_size_t, ptr, ptr),
        "delete_attrs": bind(k32, "DeleteProcThreadAttributeList", None, ptr),
        "create_job": bind(k32, "CreateJobObjectW", handle, ptr, string),
        "set_job": bind(k32, "SetInformationJobObject", w.BOOL, handle, dword, ptr, dword),
        "assign_job": bind(k32, "AssignProcessToJobObject", w.BOOL, handle, handle),
        "kill_job": bind(k32, "TerminateJobObject", w.BOOL, handle, w.UINT),
        "close": bind(k32, "CloseHandle", w.BOOL, handle),
        "create_mutex": bind(k32, "CreateMutexW", handle, ptr, w.BOOL, string),
        "release_mutex": bind(k32, "ReleaseMutex", w.BOOL, handle),
        "create_process": bind(k32, "CreateProcessW", w.BOOL, string, string, ptr, ptr,
                               w.BOOL, dword, ptr, string, c.POINTER(_Startup),
                               c.POINTER(_Process)),
        "kill_process": bind(k32, "TerminateProcess", w.BOOL, handle, w.UINT),
        "resume": bind(k32, "ResumeThread", dword, handle),
        "wait": bind(k32, "WaitForSingleObject", dword, handle, dword),
        "exit_code": bind(k32, "GetExitCodeProcess", w.BOOL, handle, c.POINTER(dword)),
    }
    return native


def system_directory() -> Path:
    buffer = c.create_unicode_buffer(512)
    size = _native()["system_dir"](buffer, len(buffer))
    _check(1 <= size < len(buffer), "could not find System32")
    return Path(buffer.value)


@contextmanager
def single_sandbox_slot():
    api = _native()
    mutex = api["create_mutex"](None, False, r"Local\AXDevFactory.SandboxCoding")
    _check(mutex, "could not create the Sandbox queue mutex")
    try:
        if api["wait"](mutex, 0) not in (0, 0x80):
            raise ContractError("another AXDEV Windows Sandbox queue is active")
        try:
            yield
        finally:
            api["release_mutex"](mutex)
    finally:
        api["close"](mutex)


@contextmanager
def _profile(tree: Path):
    native = _native()
    name = "AxdevReview." + uuid.uuid4().hex
    sid = w.LPVOID()
    result = native["create_profile"](name, name, name, None, 0, c.byref(sid))
    _check(result == 0 and sid, f"could not create profile {result & 0xffffffff:#x}")
    try:
        sid_text = w.LPWSTR()
        _check(native["sid_text"](sid, c.byref(sid_text)), "could not convert profile SID")
        try:
            grant = subprocess.run(
                [str(system_directory() / "icacls.exe"), str(tree), "/grant",
                 f"*{sid_text.value}:(OI)(CI)(RX)"], cwd=tree,
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, timeout=15, check=False)
            _check(grant.returncode == 0, "could not grant scratch read access")
        finally:
            native["free"](c.cast(sid_text, w.LPVOID))
        yield native, sid
    finally:
        native["free_sid"](sid)
        _check(native["delete_profile"](name) == 0, "could not remove temporary profile")


def run_restricted(argv: list[str], tree: Path, cwd: Path, timeout: int) -> tuple[int, bytes]:
    """Grant only read/execute on a disposable copy. Return kernel exit + bounded pipe."""
    if os.name != "nt":
        raise ContractError("Windows AppContainer reviewer requires Windows")
    import msvcrt

    executable = Path(argv[0]).resolve(strict=True)
    if tree.resolve(strict=True) not in executable.parents:
        raise ContractError("review executable is not in the private staged runtime")
    with _profile(tree) as (api, sid), ExitStack() as cleanup:
        pipe_read, pipe_write = os.pipe()
        reader = cleanup.enter_context(os.fdopen(pipe_read, "rb", buffering=0))
        writer = cleanup.enter_context(os.fdopen(pipe_write, "wb", buffering=0))
        no_input = cleanup.enter_context(open(os.devnull, "rb"))
        stdin = msvcrt.get_osfhandle(no_input.fileno())
        stdout = msvcrt.get_osfhandle(writer.fileno())
        os.set_handle_inheritable(stdin, True)
        os.set_handle_inheritable(stdout, True)

        size = c.c_size_t()
        api["init_attrs"](None, 2, 0, c.byref(size))
        attributes = c.create_string_buffer(size.value)
        _check(api["init_attrs"](attributes, 2, 0, c.byref(size)), "could not create attributes")
        cleanup.callback(api["delete_attrs"], attributes)
        handles = (w.HANDLE * 2)(stdin, stdout)
        capabilities = _Capabilities(sid, None, 0, 0)
        for attribute, value in ((0x20002, handles), (0x20009, capabilities)):
            _check(api["set_attr"](attributes, 0, attribute, c.byref(value),
                                   c.sizeof(value), None, None), "could not restrict process")

        job = api["create_job"](None, None)
        _check(job, "could not create job")
        cleanup.callback(api["close"], job)
        limits = _JobLimits()
        # KILL_ON_JOB_CLOSE, ACTIVE_PROCESS, JOB_MEMORY. Descendants cannot break away.
        limits.flags = 0x2000 | 0x8 | 0x200
        limits.processes = 4
        limits.job_memory = 512 * 1024 * 1024
        _check(api["set_job"](job, 9, c.byref(limits), c.sizeof(limits)), "could not set job limits")

        start = _Startup()
        start.size, start.placement[7] = c.sizeof(start), 0x100  # STARTF_USESTDHANDLES
        start.stdin, start.stdout, start.stderr = stdin, stdout, stdout
        start.attributes = c.cast(attributes, w.LPVOID)
        process = _Process()
        system = system_directory()
        variables = {"SYSTEMROOT": str(system.parent), "WINDIR": str(system.parent),
                     "SYSTEMDRIVE": system.drive, "PATH": str(system),
                     "USERPROFILE": str(tree), "LOCALAPPDATA": str(tree),
                     "APPDATA": str(tree), "TEMP": str(tree), "TMP": str(tree),
                     "PYTHONIOENCODING": "utf-8"}
        environment = c.create_unicode_buffer("\0".join(f"{k}={v}" for k, v in
                                                         sorted(variables.items())) + "\0\0")
        command_line = c.create_unicode_buffer(subprocess.list2cmdline(argv))
        # Extended startup info, unicode environment, no window, suspended.
        flags = 0x80000 | 0x400 | 0x8000000 | 0x4
        _check(api["create_process"](str(executable), command_line, None, None, True,
                                     flags, environment, str(cwd), c.byref(start),
                                     c.byref(process)), "could not launch restricted command")
        cleanup.callback(api["close"], process.process)
        cleanup.callback(api["close"], process.thread)
        if not api["assign_job"](job, process.process):
            api["kill_process"](process.process, 1)
            _check(False, "could not contain process job")
        cleanup.callback(api["kill_job"], job, 1)
        writer.close()

        output = bytearray()
        overflow = threading.Event()

        def receive():
            while chunk := reader.read(4096):
                output.extend(chunk)
                if len(output) > 65536:
                    overflow.set()
                    api["kill_job"](job, 1)
                    break

        read_thread = threading.Thread(target=receive, daemon=True)
        read_thread.start()
        try:
            _check(api["resume"](process.thread) != 0xffffffff, "could not start job")
            outcome = api["wait"](process.process, timeout * 1000)
            if outcome == 0x102:
                raise ContractError("Windows reviewer timed out")
            _check(outcome == 0, "could not wait for command")
            exit_code = w.DWORD()
            _check(api["exit_code"](process.process, c.byref(exit_code)), "could not read exit code")
        finally:
            api["kill_job"](job, 1)
            read_thread.join(5)
        if read_thread.is_alive() or overflow.is_set():
            raise ContractError("Windows reviewer output exceeded its limit")
        return exit_code.value, bytes(output)
