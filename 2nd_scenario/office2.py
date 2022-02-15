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


class SimpleSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    finals=["00:00:00:00:00:05","00:00:00:00:00:06","00:00:00:00:00:07"]

    hosts=["00:00:00:00:00:01","00:00:00:00:00:02","00:00:00:00:00:03","00:00:00:00:00:04",
           "00:00:00:00:00:05","00:00:00:00:00:06","00:00:00:00:00:07","00:00:00:00:00:08",
           "00:00:00:00:00:09","00:00:00:00:00:0a","00:00:00:00:00:0b","00:00:00:00:00:0c",
           "00:00:00:00:00:0d","00:00:00:00:00:0e","00:00:00:00:00:0f"]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch, self).__init__(*args, **kwargs)

        # outport = self.mac_to_port[dpid][mac_address]
        self.mac_to_port = {
            8: {"00:00:00:00:00:05": 4},
            9: {"00:00:00:00:00:06": 4, "00:00:00:00:00:07": 5}
        }

        # out_port = slice_to_port[dpid][in_port]
        #for switch 8 and 9, the default link in the link for icmp packets
        self.slice_to_port = {
            7: {1: 2, 2: 1},
            8: {4: 2},
            9: {4: 2, 5: 2},
            10: {2: 3, 3: 2, 4: 0, 1: 0}
        }

        self.end_switches=[10]

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
        
        self.logger.info("packet in %s %s %s %s", dpid, src, dst, msg.in_port)

        if dpid==10 and (msg.in_port==2 or msg.in_port==3) and dst not in self.finals:
            return

        out_port = 0

        #In this case I have to control the packet type to forward in the correct link

        if dpid in self.end_switches:
            out_port = self.slice_to_port[dpid][msg.in_port]
            if pkt.get_protocol(udp.udp):
                protocol= 1 #udp
            elif pkt.get_protocol(tcp.tcp):
                protocol=2 #tcp
            else:
                protocol=3 #icmp
        elif dpid in self.mac_to_port:
            if dst in self.mac_to_port[dpid]:
                out_port = self.mac_to_port[dpid][dst]
                if pkt.get_protocol(udp.udp):
                    protocol= 1 #udp
                elif pkt.get_protocol(tcp.tcp):
                    protocol=2 #tcp
                else:
                    protocol=3 #icmp
            elif (dpid==8 and msg.in_port== 4) or (dpid==9 and (msg.in_port==4 or msg.in_port==5)):
                #depending on the protocol, choose the link
                if pkt.get_protocol(udp.udp):
                    out_port=3
                    protocol= 1 #udp
                elif pkt.get_protocol(tcp.tcp):
                    out_port=1
                    protocol=2 #tcp
                else:
                    out_port = self.slice_to_port[dpid][msg.in_port]
                    protocol=3 #icmp
            else: 
                return
        else:
            out_port = self.slice_to_port[dpid][msg.in_port]
            if pkt.get_protocol(udp.udp):
                protocol= 1 #udp
            elif pkt.get_protocol(tcp.tcp):
                protocol=2 #tcp
            else:
                protocol=3 #icmp




        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        # in this flow table, we set also the protocol for every packet to create different rules for different packet types
        if out_port != ofproto.OFPP_FLOOD and out_port !=0 and src in self.hosts and dst in self.hosts:
            self.add_flow(datapath, msg.in_port, dst, src, actions, protocol)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.in_port,
            actions=actions, data=data)
        if out_port!=0:
            datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def _port_status_handler(self, ev):
        msg = ev.msg
        reason = msg.reason
        port_no = msg.desc.port_no

        ofproto = msg.datapath.ofproto
        if reason == ofproto.OFPPR_ADD:
            self.logger.info("port added %s", port_no)
        elif reason == ofproto.OFPPR_DELETE:
            self.logger.info("port deleted %s", port_no)
        elif reason == ofproto.OFPPR_MODIFY:
            self.logger.info("port modified %s", port_no)
        else:
            self.logger.info("Illeagal port state %s %s", port_no, reason)