#!/usr/bin/python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink


class NetworkSlicingTopo(Topo):
    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Create template host, switch, and link
        host_config = dict(inNamespace=True)
        simple_link_config = dict(bw=5)
        video_link_config = dict(bw=10)
        http_link_config = dict(bw=7)
        comm_link_config = dict(bw=5)
        connecting_slice_link_config = dict(bw=10)
        host_link_config = dict()

        # Create 14 switch nodes 
        for i in range(11):
            sconfig = {"dpid": "%016x" % (i + 1)}
            self.addSwitch("s%d" % (i + 1), protocols="OpenFlow10",**sconfig)

        # Create 14 host nodes
        for i in range(15):
            self.addHost("h%d" % (i + 1), **host_config)

        # Add switch links for slice left_up
        self.addLink("s1", "s3", **simple_link_config)
        self.addLink("s2", "s3", **simple_link_config)
        # Add switch links for slice left_down
        self.addLink("s4", "s3", **simple_link_config)
        self.addLink("s5", "s3", **simple_link_config)
        self.addLink("s4", "s5", **simple_link_config)
        # Add switch links for connecting_slice
        self.addLink("s2", "s6", **connecting_slice_link_config)
        self.addLink("s6", "s10", **connecting_slice_link_config)
        # Add switch links for slice right_up
        self.addLink("s8", "s7", **http_link_config)
        self.addLink("s7", "s9", **http_link_config)
        self.addLink("s8", "s9", **comm_link_config)
        self.addLink("s10", "s8", **video_link_config)
        self.addLink("s10", "s9", **video_link_config)
        self.addLink("s10", "s11", **simple_link_config)

        # Add host links
        self.addLink("h1", "s1", **host_link_config)
        self.addLink("h2", "s2", **host_link_config)
        self.addLink("h3", "s4", **host_link_config)
        self.addLink("h4", "s5", **host_link_config)
        self.addLink("h5", "s8", **host_link_config)
        self.addLink("h6", "s9", **host_link_config)
        self.addLink("h7", "s9", **host_link_config)
        self.addLink("h8", "s11", **host_link_config)
        self.addLink("h9", "s11", **host_link_config)
        self.addLink("h10", "s11", **host_link_config)
        self.addLink("h11", "s11", **host_link_config)
        self.addLink("h12", "s11", **host_link_config)
        self.addLink("h13", "s11", **host_link_config)
        self.addLink("h14", "s11", **host_link_config)
        self.addLink("h15", "s6", **host_link_config)



topos = {"networkslicingtopo": (lambda: NetworkSlicingTopo())}

if __name__ == "__main__":
    topo = NetworkSlicingTopo()
    net = Mininet(
        topo=topo,
        switch=OVSKernelSwitch,
        build=False,
        autoSetMacs=True,
        autoStaticArp=True,
        link=TCLink,
    )
    net.build()
    net.start()

    
    net['s1'].cmd("ovs-vsctl set-controller s1 tcp:127.0.0.1:6633")
    net['s1'].cmd("ovs-vsctl set-controller s2 tcp:127.0.0.1:6633")
    net['s1'].cmd("ovs-vsctl set-controller s3 tcp:127.0.0.1:6633 tcp:127.0.0.1:6634")

    net['s1'].cmd("ovs-vsctl set-controller s4 tcp:127.0.0.1:6634")
    net['s1'].cmd("ovs-vsctl set-controller s5 tcp:127.0.0.1:6634")

    net['s1'].cmd("ovs-vsctl set-controller s6 tcp:127.0.0.1:6635")

    net['s1'].cmd("ovs-vsctl set-controller s7 tcp:127.0.0.1:6636")
    net['s1'].cmd("ovs-vsctl set-controller s8 tcp:127.0.0.1:6636")
    net['s1'].cmd("ovs-vsctl set-controller s9 tcp:127.0.0.1:6636")
    net['s1'].cmd("ovs-vsctl set-controller s10 tcp:127.0.0.1:6636 tcp:127.0.0.1:6637")
    
    net['s1'].cmd("ovs-vsctl set-controller s11 tcp:127.0.0.1:6637")
    CLI(net)
    net.stop()
