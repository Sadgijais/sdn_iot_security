from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink


def build_topology():
    net = Mininet(controller=RemoteController, switch=OVSSwitch, link=TCLink)

    c0 = net.addController("c0", controller=RemoteController, ip="127.0.0.1", port=6653)

    h1 = net.addHost("h1", ip="10.0.0.1/24")
    h2 = net.addHost("h2", ip="10.0.0.2/24")

    s1 = net.addSwitch("s1")
    s2 = net.addSwitch("s2")
    s3 = net.addSwitch("s3")

    # Host-edge links
    net.addLink(h1, s1, bw=10, delay="3ms")
    net.addLink(h2, s3, bw=10, delay="3ms")

    # Two paths between s1 and s3: direct and via s2
    net.addLink(s1, s3, bw=10, delay="5ms")
    net.addLink(s1, s2, bw=10, delay="2ms")
    net.addLink(s2, s3, bw=10, delay="2ms")

    net.start()

    for sw in (s1, s2, s3):
        sw.cmd("ovs-vsctl set bridge {} protocols=OpenFlow13".format(sw.name))

    print("Topology started. Hosts: h1(10.0.0.1), h2(10.0.0.2)")
    print("Use Mininet CLI to run your sender/receiver transport commands.")
    CLI(net)
    net.stop()


if __name__ == "__main__":
    build_topology()
