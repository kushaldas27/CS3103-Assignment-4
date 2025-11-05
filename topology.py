from mininet.net import Mininet
from mininet.node import Controller, OVSController
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import os
import time
import sys

# check correct args
if len(sys.argv) != 4:
    print("Usage: sudo python3 topology.py <delay_ms> <jitter_ms> <loss_percent>")
    sys.exit(1)

# parse args
delay = sys.argv[1] + "ms"
jitter = sys.argv[2] + "ms"
loss = float(sys.argv[3])

# set paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(PROJECT_ROOT, 'venv', 'bin', 'python3')
server = os.path.join(PROJECT_ROOT, 'server-demo.py')
client = os.path.join(PROJECT_ROOT, 'client-demo.py')

def simple_topology():
    net = Mininet(link=TCLink)

    s1 = net.addSwitch('s1', failMode='standalone')

    # server is 1, client is 2
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')

    net.addLink(h1, s1, delay=delay, jitter=jitter, loss=loss)
    net.addLink(h2, s1, delay=delay, jitter=jitter, loss=loss)

    net.start()
    
    # run the sender/receiver on the two hosts
    h1.cmd(f'cd {PROJECT_ROOT} && {VENV_PYTHON} -u {server} > server.log 2>&1 &')
    time.sleep(0.2)
    h2.cmd(f'cd {PROJECT_ROOT} && {VENV_PYTHON} -u {client} > client.log 2>&1 &')

    CLI(net)

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    simple_topology()
