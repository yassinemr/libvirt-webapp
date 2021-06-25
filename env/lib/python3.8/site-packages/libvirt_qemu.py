#
# WARNING WARNING WARNING WARNING
#
# This file is automatically written by generator.py. Any changes
# made here will be lost.
#
# To change the manually written methods edit libvirt-qemu-override.py
# To change the automatically written methods edit generator.py
#
# WARNING WARNING WARNING WARNING
#
# Automatically written part of python bindings for libvirt
#
try:
    import libvirtmod_qemu
except ImportError as lib_e:
    try:
        import cygvirtmod_qemu as libvirtmod_qemu
    except ImportError as cyg_e:
        if "No module named" in str(cyg_e):
            raise lib_e

import libvirt

# WARNING WARNING WARNING WARNING
#
# Manually written part of python bindings for libvirt-qemu
from typing import Any, Callable, Dict


def _dispatchQemuMonitorEventCallback(conn: libvirt.virConnect, dom: libvirt.virDomain, event: str, seconds: int, micros: int, details: str, cbData: Dict[str, Any]) -> int:
    """Dispatches events to python user qemu monitor event callbacks
    """
    cb = cbData["cb"]
    opaque = cbData["opaque"]

    cb(conn, libvirt.virDomain(conn, _obj=dom), event, seconds, micros, details, opaque)
    return 0


def qemuMonitorEventDeregister(conn: libvirt.virConnect, callbackID: int) -> None:
    """Removes a qemu monitor event callback. De-registering for a callback
       will disable delivery of this event type"""
    try:
        ret = libvirtmod_qemu.virConnectDomainQemuMonitorEventDeregister(conn._o, callbackID)
        if ret == -1:
            raise libvirt.libvirtError('virConnectDomainQemuMonitorEventDeregister() failed')
        del conn.qemuMonitorEventCallbackID[callbackID]  # type: ignore
    except AttributeError:
        pass


def qemuMonitorEventRegister(conn: libvirt.virConnect, dom: libvirt.virDomain, event: str, cb: Callable[[libvirt.virConnect, libvirt.virDomain, str, int, int, str, libvirt._T], None], opaque: libvirt._T, flags: int = 0) -> int:
    """Adds a qemu monitor event callback. Registering for a monitor
       callback will enable delivery of the events"""
    if not hasattr(conn, 'qemuMonitorEventCallbackID'):
        conn.qemuMonitorEventCallbackID = {}  # type: ignore
    cbData = {"cb": cb, "conn": conn, "opaque": opaque}
    if dom is None:
        ret = libvirtmod_qemu.virConnectDomainQemuMonitorEventRegister(conn._o, None, event, cbData, flags)
    else:
        ret = libvirtmod_qemu.virConnectDomainQemuMonitorEventRegister(conn._o, dom._o, event, cbData, flags)
    if ret == -1:
        raise libvirt.libvirtError('virConnectDomainQemuMonitorEventRegister() failed')
    conn.qemuMonitorEventCallbackID[ret] = opaque  # type: ignore
    return ret
#
# WARNING WARNING WARNING WARNING
#
#
# Functions from module libvirt-qemu
#

def qemuAgentCommand(domain, cmd, timeout, flags):
    """Send a Guest Agent command to domain """
    ret = libvirtmod_qemu.virDomainQemuAgentCommand(domain._o, cmd, timeout, flags)
    if ret is None:
        raise libvirt.libvirtError('virDomainQemuAgentCommand() failed')
    return ret

def qemuAttach(conn, pid_value, flags):
    """This API is QEMU specific, so it will only work with hypervisor
    connections to the QEMU driver.
    
    This API will attach to an externally launched QEMU process
    identified by @pid. There are several requirements to successfully
    attach to an external QEMU process:
    
      - It must have been started with a monitor socket using the UNIX
        domain socket protocol.
      - No device hotplug/unplug, or other configuration changes can
        have been made via the monitor since it started.
      - The '-name' and '-uuid' arguments should have been set (not
        mandatory, but strongly recommended)
    
    To date, the only platforms we know of where pid_t is larger than
    unsigned int (64-bit Windows) also lack UNIX sockets, so the choice
    of @pid_value as an unsigned int should not present any difficulties.
    
    If successful, then the guest will appear in the list of running
    domains for this connection, and other APIs should operate
    normally (provided the above requirements were honored). """
    ret = libvirtmod_qemu.virDomainQemuAttach(conn._o, pid_value, flags)
    if ret is None:
        raise libvirt.libvirtError('virDomainQemuAttach() failed')
    __tmp = libvirt.virDomain(conn, _obj=ret)
    return __tmp

def qemuMonitorCommand(domain, cmd, flags):
    """Send an arbitrary monitor command through qemu monitor of domain """
    ret = libvirtmod_qemu.virDomainQemuMonitorCommand(domain._o, cmd, flags)
    if ret is None:
        raise libvirt.libvirtError('virDomainQemuMonitorCommand() failed')
    return ret

# virConnectDomainQemuMonitorEventRegisterFlags
VIR_CONNECT_DOMAIN_QEMU_MONITOR_EVENT_REGISTER_REGEX = 1
VIR_CONNECT_DOMAIN_QEMU_MONITOR_EVENT_REGISTER_NOCASE = 2

# virDomainQemuAgentCommandTimeoutValues
VIR_DOMAIN_QEMU_AGENT_COMMAND_BLOCK = -2
VIR_DOMAIN_QEMU_AGENT_COMMAND_MIN = -2
VIR_DOMAIN_QEMU_AGENT_COMMAND_DEFAULT = -1
VIR_DOMAIN_QEMU_AGENT_COMMAND_NOWAIT = 0
VIR_DOMAIN_QEMU_AGENT_COMMAND_SHUTDOWN = 60

# virDomainQemuMonitorCommandFlags
VIR_DOMAIN_QEMU_MONITOR_COMMAND_DEFAULT = 0
VIR_DOMAIN_QEMU_MONITOR_COMMAND_HMP = 1

