#!/usr/bin/python3
import ctypes
import os
import sys

# Constants
CLONE_NEWUSER = 0x10000000
CLONE_NEWNET = 0x40000000
CLONE_NEWIPC = 0x08000000
IFNAMSIZ = 16
SIOCGIFFLAGS = 0x8913
SIOCSIFFLAGS = 0x8914
IFF_LOOPBACK = 0x8
IFF_MULTICAST = 0x1000
IFF_UP = 0x1
AF_INET = 2
SOCK_DGRAM = 2

# Structures
class sockaddr(ctypes.Structure):
    pass

sockaddr._fields_ = [("sa_family", ctypes.c_ushort), ("sa_data", ctypes.c_char * 14)]

class ifreq(ctypes.Structure):
    _fields_ = [("ifr_name", ctypes.c_char * IFNAMSIZ), ("ifr_flags", ctypes.c_short)]

class ifaddrs(ctypes.Structure):
    pass

ifaddrs._fields_ = [
    ("ifa_next", ctypes.POINTER(ifaddrs)),
    ("ifa_name", ctypes.c_char_p),
    ("ifa_flags", ctypes.c_uint),
    ("ifa_addr", ctypes.POINTER(sockaddr)),
    ("ifa_netmask", ctypes.POINTER(sockaddr)),
    ("ifa_ifu", ctypes.c_uint * 4),  # Union for ifa_broadaddr and ifa_dstaddr
    ("ifa_data", ctypes.c_void_p),
]

# Functions
libc = ctypes.CDLL("libc.so.6")

def error(message):
    print("create_linux_namespaces:", message, ":", os.strerror(ctypes.get_errno()))

def create_linux_namespaces():
    result = libc.unshare(CLONE_NEWUSER | CLONE_NEWNET | CLONE_NEWIPC)
    if result != 0:
        error("failed to call unshare")
        return False

    # Assert there is exactly one network interface
    ifaddr = ctypes.POINTER(ifaddrs)()
    if libc.getifaddrs(ctypes.byref(ifaddr)) == -1:
        error("could not get network interfaces")
        return False

    current_ifaddr = ifaddr.contents

    if current_ifaddr is None:
        error("there are no network interfaces")
        return False

    if bool(current_ifaddr.ifa_next):
        error("there are multiple network interfaces")
        return False

    # Need a socket to do ioctl stuff on
    fd = libc.socket(AF_INET, SOCK_DGRAM, 0)
    if fd < 0:
        error("could not open a socket")
        libc.freeifaddrs(ifaddr)
        return False

    ioctl_request = ifreq()

    # Check what flags are set on the interface
    ioctl_request.ifr_name = current_ifaddr.ifa_name
    err = libc.ioctl(fd, SIOCGIFFLAGS, ctypes.byref(ioctl_request))
    if err != 0:
        libc.freeifaddrs(ifaddr)
        error("failed to get interface flags")
        return False

    # Expecting a loopback interface.
    if not (ioctl_request.ifr_flags & IFF_LOOPBACK):
        error("the only interface is not a loopback interface")
        libc.freeifaddrs(ifaddr)
        return False

    # Enable multicast
    ioctl_request.ifr_flags |= IFF_MULTICAST
    # Bring up interface
    ioctl_request.ifr_flags |= IFF_UP

    err = libc.ioctl(fd, SIOCSIFFLAGS, ctypes.byref(ioctl_request))
    if err != 0:
        error("failed to set interface flags")
        libc.freeifaddrs(ifaddr)
        return False

    libc.freeifaddrs(ifaddr)
    return True

def main():
    if os.name != 'posix':
        error("Not suported on non posix systems")

    if len(sys.argv) < 2:
        print("shim must be given a command to execute")
        exit(-1)

    if not create_linux_namespaces():
        error("Failed to fully create isolated environment")

    os.execv(sys.argv[1], sys.argv[1:])
