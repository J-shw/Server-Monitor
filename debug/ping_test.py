
from icmplib import ping
import time

while True:
    host = ping('10.0.3.1', count=1, timeout=2)  # Ping once with a 2-second timeout

    if host.is_alive:
        print(f"Average RTT: {host.avg_rtt} ms")
    else:
        print('Dead')
    time.sleep(5)


