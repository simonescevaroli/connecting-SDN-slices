# Connecting SDN Slices

### TABLE OF CONTENTS<br>
[Components used](https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/README.md#components-used)<br>
[1st topology](https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/README.md#1st-topology)<br>
 - [Statement](https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/README.md#statement-general-idea)<br>
 - [Topology](https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/README.md#topology)<br>
 - [Demo](https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/README.md#demo)<br>
   - [Set up the environment](https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/README.md#set-up-the-environment)<br>
   - [Set up the topology in mininet](https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/README.md#set-up-the-topology-in-mininet)<br>
   - [Set up the controllers](https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/README.md#set-up-the-controllers)<br>
   - [Test reachability](https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/README.md#test-reachability)<br>
   - [Close and clean everything up](https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/README.md#close-and-clean-up-everything)<br>

[2nd topology](https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/README.md#2nd-topology)<br>
 - [Statement](https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/README.md#statement-general-idea-1)<br>
 - [Topology](https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/README.md#topology-1)<br>
 - [Demo](https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/README.md#demo-1)<br>
   - [Set up the environment](https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/README.md#set-up-the-environment-1)<br>
   - [Set up the topology in mininet](https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/README.md#set-up-the-topology-in-mininet-1)<br>
   - [Set up the controllers](https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/README.md#set-up-the-controllers-1)<br>
   - [Test reachability](https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/README.md#test-reachability-1)<br>
   - [Close and clean everything up](https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/README.md#close-and-clean-up-everything-1)<br>



### COMPONENTS USED<br>
• **Open vSwitch**<br>
• **RYU controller**: defined in ComNetsEmu<br>
• **Host and switches**: defined in ComNetsEmu<br>
• **OpenFlow 1.0** (both RYU controllers and OvSwitches need to be set up working with this version)<br>


## 1st topology

### STATEMENT (GENERAL IDEA)<br>
• Here we have a cycle. Every host can communicate with the others, but when a flood starts we enter in an infinite loop<br>
<img src="https://user-images.githubusercontent.com/98694899/153767602-b65255fd-3629-4aeb-96d0-10c3fbfa93dc.jpg" width="30%" height="30%">

<br>• A topology slicing avoids infinite loops by separating the cycle into two trees, controlled by two controllers; the two slices cannot communicate <br>
<img src="https://user-images.githubusercontent.com/98694899/153768938-7c482ef2-37e2-470a-ac6d-09e848209593.jpg" width="30%" height="30%">

<br>• We interconnected the two slices by adding a common root (s9); a third controller manages inter-slices communication<br>
<img src="https://user-images.githubusercontent.com/98694899/153833287-51bb54d8-f1d5-4a97-a9f4-b2ff06432ff0.jpeg" width="50%" height="50%">

<br>• Additionally, the provider doesn’t want a slice to send UDP packets to the other; s9 sends the inter-slices UDP packets to a server that filters (and then drops) the packets<br>
<br>
### TOPOLOGY<br>
<img src="https://user-images.githubusercontent.com/98694899/154034712-90fce033-2d10-49f8-9502-3fadf188d858.png" width="100%" height="100%">
To see further details see <a href="https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/1st_topology.png" target="_blank" >1st_topology</a>
<br>

We realized three different slices (topology slicing):<br>
- **slice1**: a controller allows the communication between: h1, h2, h5, h6<br>
- **slice2**: a controller allows the communication between: h3, h4, h7, h8<br>
- **connecting_slice**: a controller allows non-UDP packet inter-slices transmission, and filters UDP packet to server1 and server2 (if sent by slice1 or slice2 respectively)<br>
<br>_Note_: server1 and server2 are configured not to send any packet. They can only receive UDP packets that are filtered by s9<br>
<br>

### DEMO<br>
#### Set up the environment<br>
Start up the VM<br>
```vagrant up comnetsemu```<br><br>
Log into the VM<br>
```vagrant ssh comnetsemu```<br>
<br>
#### Set up the topology in mininet<br>
Flush any previous configuration<br>
```$ sudo mn -c```<br><br>
Build the topology<br>
```$ sudo python3 network.py```<br>
<br>
#### Set up the controllers
In a new terminal, run this script to start all the controllers in a single shell<br>
```./runcontrollers.py```<br>
<br>
Create a new terminal for future flow table test<br>
<br>
#### Test reachability<br>
By running  ```mininet> pingall```  we obtain the following result:<br>
<img src="https://user-images.githubusercontent.com/98694899/153769411-7121dee2-2ae4-4369-9dd4-355b68d1915d.png" width="30%" height="30%"><br>
_Note_: ping and pingall send ICMP packets.<br>
_Note_: server1 and server2 never send and receive ICMP packets<br>

Perform ping between host 1 and host 2<br>
```mininet> h1 ping -c3 h2```<br>
<img src="https://user-images.githubusercontent.com/98694899/153769590-d612d838-37de-40ea-aab7-c5e69427884a.png" width="60%" height="60%">

Perform ping between host 3 and host 4<br>
```mininet> h3 ping -c3 h4```<br>
<img src="https://user-images.githubusercontent.com/98689485/154051445-bc7f9811-df7d-4ff7-8dba-cd908d810eda.png" width="60%" height="60%">
<br><br>
Intra-slice communication works correctly.<br>

Show s4 flow table<br>
```$ sudo ovs-ofctl dump-flows s4```<br>
<img src="https://user-images.githubusercontent.com/98694899/153769807-7fe49a24-de63-453c-a20b-c13f79780c2b.png" width="100%" height="100%">

Host 1 can send TCP packets to Host 4<br>
```mininet> h4 iperf -s &```<br>
```mininet> h1 iperf -c 10.0.0.4 -t 5 -i 1```<br>
<img src="https://user-images.githubusercontent.com/98694899/153769940-f1cd07a1-a8a1-418e-af0c-e7e4bd2c4231.png" width="40%" height="40%">

Host 1 cannot send UDP packets to Host 3<br>
```mininet> h3 iperf -s -u &```<br>
```mininet> h1 iperf -c -u 10.0.0.3 -u -t 5 -i 1```<br>
<img src="https://user-images.githubusercontent.com/98689485/154041334-74617265-4e63-4636-892f-4f749507aeee.png" width="40%" height="40%">

	
Show s9 flow table (path depends on protocol)<br>
```$ sudo ovs-ofctl dump-flows s9```<br>
<img src="https://user-images.githubusercontent.com/98694899/153770285-680e26cf-61c8-4198-a31a-6316ea2802c2.png" width="100%" height="100%">
<br><br>
#### Close and clean up everything<br>
It’s better to flush the topology with  ```sudo mn -c```  and to stop the VM with  ```vagrant halt comnetsemu```	








## 2nd topology

### STATEMENT (GENERAL IDEA)<br>
• Here we have two separate networks.<br>
<img src="https://user-images.githubusercontent.com/98694899/154029905-d5c731e6-3058-45f3-aa0d-12e1b59d7b82.jpg" width="30%" height="30%">

<br>• We performed a topology slicing in each network. We also wanted to connect two slices with a third one.<br>
_Note_: 2 slices remain separated, and use their own logic (see the image below).<br>
<br>

### TOPOLOGY<br>

<img src="https://user-images.githubusercontent.com/98694899/154034840-1564d1c8-4b3d-4a97-b68a-2bf67caede40.png" width="100%" height="100%"><br>

To see further details see <a href="https://github.com/elisacomposta/ConnectingSDNSlices/blob/main/2nd_topology.png">2nd_topology</a>
<br>

We realized five different slices:<br>
- **control_office**: a controller allows the communication between: h1, h2<br>
- **office1**: a controller allows the communication between: h3, h4. Each packet follows a specific path<br>
- **office2**: a controller allows the communication between: h5, h6, h7. The path depends on the packet protocol (service slicing)<br>
- **computer_room**: a controller allows the communication between: h8, h9, h10, h11, h12, h13, h14<br>
- **connecting_slice**: a controller allows the communication between the slices _control_office_ and _computer_room_<br><br>
_Note_: _office1_ slice contains a loop; this doesn't cause any problem since each packet follows a specific path<br>
<br>

### DEMO<br>
#### Set up the topology in mininet<br>
Flush any previous configuration<br>
```$ sudo mn -c```<br><br>
Build the topology<br>
```$ sudo python3 network.py```<br>
<br>
#### Set up the controllers
In a new terminal, run this script to start all the controllers in a single shell<br>
```./runcontrollers.py```<br>
<br>
Create a new terminal for future flow table test<br>
<br>
#### Test reachability<br>
By running  ```mininet> pingall```  we obtain the following result:<br>
<img src="https://user-images.githubusercontent.com/98689485/154036606-263c34d0-8db7-4765-a118-04ac63ca1fad.png" width="30%" height="30%">

Perform ping between host 1 and host 2<br>
```mininet> h1 ping -c3 h2```<br>
<img src="https://user-images.githubusercontent.com/98689485/154036720-28756291-41ab-4fae-a07b-857fbfe87347.png" width="40%" height="40%"><br>

Perform ping between host 3 and host 4<br>
```mininet> h3 ping -c3 h4```<br>
<img src="https://user-images.githubusercontent.com/98689485/154036785-cd23669e-032d-4213-8db0-41d8d34f3db9.png " width="40%" height="40%"><br>

Intra-slice communication works correctly.<br>

Show s3 flow table<br>
```$ sudo ovs-ofctl dump-flows s3```<br>
<img src="https://user-images.githubusercontent.com/98689485/154037351-3b76435e-d190-42e7-a43a-f2f0b2eb819c.png" width="100%" height="100%"><br>

Show s4 flow table<br>
```$ sudo ovs-ofctl dump-flows s4```<br>
<img src="https://user-images.githubusercontent.com/98689485/154037460-4078aa8a-64c5-401b-976c-b6047457d42f.png" width="100%" height="100%"><br>

Perform ping between host 2 and host 11<br>
```mininet> h2 ping -c3 h11```<br>
<img src="https://user-images.githubusercontent.com/98689485/154038013-6194deb8-7fba-447f-ab78-6aac3a24a6c1.png" width="40%" height="40%"><br>

Also inter-slice communication works correctly (passing through connecting_slice).<br><br>

Now let's test the reachability in the office2, depending on the packet type<br>

Perform ping between host 5 and host 7 (ICMP packets)<br>
```mininet> h5 ping -c3 h7```<br>
<img src="https://user-images.githubusercontent.com/98689485/154038489-f832991b-49d7-4541-80d8-9c4780722c08.png" width="40%" height="40%"><br>

Host 5 send UDP packets to Host 7<br>
```mininet> h7 iperf -s -u -b 10M &```<br>
```mininet> h5 iperf -c 10.0.0.7 -u -b 10M -t 10 -i 1```<br>
<img src="https://user-images.githubusercontent.com/98689485/154039193-214d5261-aa2c-45f4-813b-ac77f5fe60f9.png" width="40%" height="40%">

Host 5 send TCP packets to Host 7<br>
```mininet> h7 iperf -s -b 7M &```<br>
```mininet> h5 iperf -c 10.0.0.7 -b 7M -t 10 -i 1```<br>
<img src="https://user-images.githubusercontent.com/98689485/154039572-a943c9c3-3eda-4e49-8ce3-83158912a24f.png" width="40%" height="40%">

Show s8 flow table<br>
```$ sudo ovs-ofctl dump-flows s8```<br>
<img src="https://user-images.githubusercontent.com/98689485/154041830-157b75ee-a1ff-417b-bf6c-8c03b1795962.png" width="100%" height="100%"><br>
This switch also saves the packet type so that a packet can choose the correct entry depending on that<br>

Show s10 flow table<br>
```$ sudo ovs-ofctl dump-flows s10```<br>
<img src="https://user-images.githubusercontent.com/98689485/154042119-2182702b-b3ae-487f-83cb-3deb88a188b5.png" width="100%" height="100%"><br>

#### Close and clean up everything<br>
It’s better to flush the topology with  ```sudo mn -c```  and to stop the VM with  ```vagrant halt comnetsemu```	
