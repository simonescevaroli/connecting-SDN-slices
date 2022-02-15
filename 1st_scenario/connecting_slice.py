from typing import Protocol
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import udp
from ryu.lib.packet import tcp
from ryu.lib.packet import icmp


class SimpleSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    servers=["00:00:00:00:00:09","00:00:00:00:00:0a"]
    hosts=["00:00:00:00:00:01","00:00:00:00:00:02","00:00:00:00:00:03","00:00:00:00:00:04",
           "00:00:00:00:00:05","00:00:00:00:00:06","00:00:00:00:00:07","00:00:00:00:00:08"]

    hostSlice1=["00:00:00:00:00:01","00:00:00:00:00:02","00:00:00:00:00:05","00:00:00:00:00:06"]
    hostSlice2=["00:00:00:00:00:03","00:00:00:00:00:04","00:00:00:00:00:07","00:00:00:00:00:08"]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch, self).__init__(*args, **kwargs)

        self.mac_to_port = {
        }

        # out_port = slice_to_port[dpid][in_port]
        self.slice_to_port = {
            9: {1: 2, 2: 1, 3: 0, 4: 0}
        }

    def add_flow(self, datapath, in_port, dst, src, actions, protocol):
        ofproto = datapath.ofproto
        if protocol ==1: #udp
            proto=0x11
        elif protocol ==2: #tcp
            proto=0x06
        else: #icmp
            proto=0x01

        match = datapath.ofproto_parser.OFPMatch(
            in_port=in_port,
            dl_dst=haddr_to_bin(dst), dl_src=haddr_to_bin(src),
            dl_type=ether_types.ETH_TYPE_IP,
            nw_proto=proto)

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=ofproto.OFP_DEFAULT_PRIORITY,
            flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = msg.in_port

        self.logger.info("LOG s%s received packet (in_port=%s)", dpid, msg.in_port)

        out_port=0

        #drop packet when the destination is not in the other slice
        if (msg.in_port == 1 and dst in self.hostSlice1) or (msg.in_port == 2 and dst in self.hostSlice2):
            return

        #filter the udp packets, sending them to the corresponding server
        if pkt.get_protocol(udp.udp) and msg.in_port != 3 and msg.in_port != 4:
            out_port=2+msg.in_port #if arrives from slice1, send to server1 etc
            protocol=1      #udp
        else:
            out_port = self.slice_to_port[dpid][msg.in_port]
            if pkt.get_protocol(tcp.tcp):
                protocol=2      #tcp
            else:
                protocol=3      #icmp
        

        if out_port==0 or (not pkt.get_protocol(udp.udp) and (dst in self.servers)):
            #drop packets recieved from servers (they are backup servers)
            return

        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        # install an additional column for the packet type
        if out_port != ofproto.OFPP_FLOOD and dst in self.hosts and src in self.hosts:
            self.add_flow(datapath, msg.in_port, dst, src, actions,protocol)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.in_port,
            actions=actions, data=data)
        
        self.logger.info("LOG s%s sending packet (out_port=%s)", dpid, out_port)
        datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def _port_status_handler(self, ev):
        msg = ev.msg
        reason = msg.reason
        port_no = msg.desc.port_no

        ofproto = msg.datapath.ofproto
        if reason == ofproto.OFPPR_ADD:
            self.logger.info("Port added %s", port_no)
        elif reason == ofproto.OFPPR_DELETE:
            self.logger.info("Port deleted %s", port_no)
        elif reason == ofproto.OFPPR_MODIFY:
            self.logger.info("Port modified %s", port_no)
        else:
            self.logger.info("Illeagal port state %s %s", port_no, reason)