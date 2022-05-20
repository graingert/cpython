# Test BaseEventLoop.getaddrinfo performance, before and after my commit 39c135b
# Try a variety of getaddrinfo parameters and log the duration of 10k calls

import socket
import time
from asyncio import get_event_loop

try:
    from asyncio.base_events import _ipaddr_info
except ImportError:
    def _ipaddr_info_cache_clear():
        return
else:
    try:
        _ipaddr_info_cache_clear = _ipaddr_info.cache_clear
    except AttributeError:
        def _ipaddr_info_cache_clear():
            return

UNSPEC = socket.AF_UNSPEC
INET = socket.AF_INET
INET6 = socket.AF_INET6
STREAM = socket.SOCK_STREAM
DGRAM = socket.SOCK_DGRAM
TCP = socket.IPPROTO_TCP
UDP = socket.IPPROTO_UDP

loop = get_event_loop()


def lookup(host=None, port=None, family=0, type=0, proto=0, flags=0):
    return loop.run_until_complete(loop.getaddrinfo(
        host, port, family=family, type=type, proto=proto, flags=flags))


async def aipaddr_info(host=None, port=None, family=0, type=0, proto=0, flags=0):
    return _ipaddr_info(host=host, port=port, family=family, type=type, proto=proto)


def loopup_inetpton(host=None, port=None, family=0, type=0, proto=0, flags=0):
    return loop.run_until_complete(aipaddr_info(
        host, port, family=family, type=type, proto=proto, flags=flags))


print('{:>10} {:>10} {:>10} {:>10} {:>10} {:>7}'.format(
    'host', 'port', 'family', 'type', 'proto', 'secs'))

for info in [
    ('1.2.3.4', 1, INET, STREAM, TCP),
    ('1.2.3.4', 1, UNSPEC, STREAM, TCP),
    ('1.2.3.4', 1, UNSPEC, DGRAM, UDP),
    # Socket type STREAM implies TCP protocol.
    ('1.2.3.4', 1, UNSPEC, STREAM, 0),
    # Socket type DGRAM implies UDP protocol.
    ('1.2.3.4', 1, UNSPEC, DGRAM, 0),
    # No socket type.
    ('1.2.3.4', 1, UNSPEC, 0, 0),
    # IPv4 address with family IPv6.
    ('::3', 1, INET6, STREAM, TCP),
    ('::3', 1, UNSPEC, STREAM, TCP),
    # IPv6 address with zone index.
    ('::3%lo0', 1, INET6, STREAM, TCP),
]:
    start = time.time()
    for _ in range(100000):
        _ipaddr_info_cache_clear()
        loopup_inetpton(*info)

    duration = time.time() - start
    print('{:>10} {:>10} {:>10} {:>10} {:>10}    {:>4.1f}'.format(
        *(info + (duration,))))
