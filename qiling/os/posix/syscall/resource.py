#!/usr/bin/env python3
#
# Cross Platform and Multi Architecture Advanced Binary Emulation Framework
#

try:
    import resource
except ImportError:
    # The library 'resource' does not exist on windows, so provide a dummy shim
    class DummyResource:
        def getrlimit(self, resource):
            return (-1, -1)
        def setrlimit(self, resource, rlim):
            pass
    resource = DummyResource()


from qiling.const import *
from qiling.os.linux.thread import *
from qiling.const import *
from qiling.os.posix.filestruct import *
from qiling.os.filestruct import *
from qiling.os.posix.const_mapping import *
from qiling.exception import *


def ql_getrlimit(ql, rlimit_resource):
    RLIMIT_STACK = 3
    if rlimit_resource == RLIMIT_STACK:
        if ql.archbit == 64:
            stack_size = int(ql.os.profile.get("OS64", "stack_size"), 16)
        elif ql.archbit == 32:
            stack_size = int(ql.os.profile.get("OS32", "stack_size"), 16)
        rlim = (stack_size, -1)
    else:
        rlim = resource.getrlimit(rlimit_resource)
    return rlim


def ql_setrlimit(ql, rlimit_resource, rlim):
    RLIMIT_STACK = 3
    if rlimit_resource == RLIMIT_STACK:
        if ql.archbit == 64:
            ql.os.profile.set("OS64", "stack_size", rlim[0])
        elif ql.archbit == 32:
            ql.os.profile.set("OS32", "stack_size", rlim[0])
    else:
        resource.setrlimit(rlimit_resource, rlim)


def ql_syscall_ugetrlimit(ql, ugetrlimit_resource, ugetrlimit_rlim, *args, **kw):
    try:
        rlim = ql_getrlimit(ql, ugetrlimit_resource)
        ql.mem.write(ugetrlimit_rlim, ql.pack32s(rlim[0]) + ql.pack32s(rlim[1]))
        regreturn = 0
    except:
        regreturn = -1
    return regreturn


def ql_syscall_getrlimit(ql, getrlimit_resource, getrlimit_rlim, *args, **kw):
    try:
        rlim = ql_getrlimit(ql, getrlimit_resource)
        ql.mem.write(getrlimit_rlim, ql.pack64s(rlim[0]) + ql.pack64s(rlim[1]))
        regreturn = 0
    except:
        regreturn = -1
    return regreturn


def ql_syscall_setrlimit(ql, setrlimit_resource, setrlimit_rlim, *args, **kw):
    # maybe we can nop the setrlimit
    try:
        tmp_rlim = (ql.unpack32s(ql.mem.read(setrlimit_rlim, 4)), ql.unpack32s(ql.mem.read(setrlimit_rlim + 4, 4)))
        ql_setrlimit(ql, setrlimit_resource, tmp_rlim)
        regreturn = 0
    except:
        regreturn = -1
    return regreturn


def ql_syscall_prlimit64(ql, prlimit64_pid, prlimit64_resource, prlimit64_new_limit, prlimit64_old_limit, *args, **kw):
    # setrlimit() and getrlimit()
    if prlimit64_pid == 0 and prlimit64_new_limit == 0:
        try:
            rlim = ql_getrlimit(ql, prlimit64_resource)
            ql.mem.write(prlimit64_old_limit, ql.packs(rlim[0]) + ql.packs(rlim[1]))
            regreturn = 0
        except:
            regreturn = -1
    else:
        # set other process which pid != 0
        regreturn = -1
    return regreturn


def ql_syscall_getpriority(ql, getpriority_which, getpriority_who, *args, **kw):
    try:
        regreturn = os.getpriority(getpriority_which, getpriority_who)
    except:
        regreturn = -1
    return regreturn
