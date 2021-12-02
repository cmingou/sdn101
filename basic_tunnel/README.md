# Implementing Basic Tunneling

## Introduction

In this exercise, we will add support for a basic tunneling protocol to the basic 
switch that you completed in the previous assignment.  The basic switch
forwards based on the ingress port.  Your jobs is to define a new
header type to encapsulate the IP packet and modify the switch code, so that it
instead decides the destination port using a new tunnel header.

The new header type will contain a protocol ID, which indicates the type of
packet being encapsulated, along with a destination ID to be used for routing.


> **Spoiler alert:** There is a reference solution in the `solution`
> sub-directory. Feel free to compare your implementation to the reference.

The starter code for this assignment is in a file called `basic_tunnel.p4` and
is simply the solution to the basic switch from the previous exercise.


### A note about the control plane

A P4 program defines a packet-processing pipeline, but the rules within each
table are inserted by the control plane. When a rule matches a packet, its
action is invoked with parameters supplied by the control plane as part of the
rule.

For this exercise, you should add the necessary control plane entries. 

**Important:** We use P4Runtime shell to install the control plane rules.

## Step 1: Implement Basic Tunneling

The `basic_tunnel.p4` file contains an implementation of a basic switch.  It
also contains comments marked with `TODO` which indicate the functionality that
you need to implement. A complete implementation of the `basic_tunnel.p4`
switch will be able to forward based on the contents of a custom encapsulation
header as well as perform normal basic switch if the encapsulation header does
not exist in the packet.

Your job will be to do the following:

1. **NOTE:** A new header type has been added called `myTunnel_t` that contains
two 16-bit fields: `proto_id` and `dst_id`.
2. **NOTE:** The `myTunnel_t` header has been added to the `headers` struct.
2. **TODO:** Update the parser to extract either the `myTunnel` header or
`ipv4` header based on the `etherType` field in the Ethernet header. The
etherType corresponding to the myTunnel header is `0x1212`. The parser should
also extract the `ipv4` header after the `myTunnel` header if `proto_id` ==
`ETHERTYPE_IPV4` (i.e.  0x0800).
3. **TODO:** Define a new action called `myTunnel_forward` that simply sets the
egress port (i.e. `ucast_egress_port` field of the `ingress_intrinsic_metadata_for_tm_t` bus) 
to the port number provided by the control plane.
4. **TODO:** Define a new table called `myTunnel_exact` that perfoms an exact
match on the `dst_id` field of the `myTunnel` header. This table should invoke
either the `myTunnel_forward` action if the there is a match in the table and
it should invoke the `drop` action otherwise.
5. **TODO:** Update the `apply` statement in the `SwitchIngress` control block to
apply your newly defined `myTunnel_exact` table if the `myTunnel` header is
valid. Otherwise, invoke the `forward` table if the `ipv4` header is valid.
6. **TODO:** Update the deparser to emit the `ethernet`, then `myTunnel`, then
`ipv4` headers. Remember that the deparser will only emit a header if it is
valid. A header's implicit validity bit is set by the parser upon extraction.
So there is no need to check header validity here.

![topology](./topo.png)

## Step 2: Run your solution

Before run solution, make sure you have a clean environment. If not please execute `stop-net` and `start-net` again.
In this lab we only need use switch1(sw1) for target.

1. In your shell, run:
   ```bash
   p4c -n basic_tunnel
   ```
   This will compile `basic_tunnel.p4` and generated output file in `./tofino` directory.

2. Due stratum support many device configuration, we should generate the protobuf based format binary. Run tofino.sh to build dev_config.pb.bin:

   ```bash
   tofino.sh -c ./tofino/basic_tunnel/basic_tunnel.conf
   ```

   This will generate device_config.pb.bin is current directory.
   
3. Run p4runtime-shell to load pipeline and add flow entries:

   ```bash
   p4rt-shell -n sw1 -i ./tofino/basic_tunnel/p4info.txt -b ./device_config.pb.bin
   P4Runtime sh >>> te = table_entry["SwitchIngress.myTunnel_exact"](action="myTunnel_forward")
   P4Runtime sh >>> te.match["hdr.myTunnel.dst_id"]="666"
   P4Runtime sh >>> te.action["port"]="4"
   P4Runtime sh >>> te.insert
   P4Runtime sh >>> table_entry["SwitchIngress.myTunnel_exact"].read(lambda te: print(te))
   table_id: 40512668 ("SwitchIngress.myTunnel_exact")
   match {
     field_id: 1 ("hdr.myTunnel.dst_id")
     exact {
       value: "\\x02\\x9a"
     }
   }
   action {
     action {
       action_id: 17926915 ("SwitchIngress.myTunnel_forward")
       params {
         param_id: 1 ("port")
         value: "\\x00\\x04"
       }
     }
   }
   ```

   This will:

   * load pipeline to sw1
   * add flow entry which match ingress port 3 and forward to port 4

4. Copy `receive.py` and `send.py` to sw1
   ```bash
   copy-to-host sw1 send.py
   copy-to-host sw1 receive.py
   copy-to-host sw1 myTunnel_header.py
   ```
5. Now we test with tunneling. In new shell, execute `attach-host sw1` and start listen message on port 4: 
  ```bash
  python ./receive.py
  ```
  The packet should be send from `veth7` to switch port 3 and forward to switch port 4 to `veth9`. 
  If you examine the received packet you should see that is consists of an Ethernet header, 
  a tunnel header, an IP header, a TCP header, and the message. 

6. In new shell, execute `attach-host sw1` and send a message: 
  ```bash
  python ./send.py 10.0.3.3 "P4 is cool" --dst_id 2
  ```
  The packet should be NOT received at `veth9`, due the dst_id is not settled by control plane. 
  This is because the switch is no longer using the IP header for routing
  when the `MyTunnel` header is in the packet. 

7. Send a message with `dst_id` 666: 
  ```bash
  python ./send.py 10.0.3.3 "P4 is cool" --dst_id 666
  ```
  The packet should be received at `veth9`, even the dst_ip_address is invalid.
  This is because the switch is no longer using the IP header for routing
  when the `MyTunnel` header is in the packet. 

8. Type `exit` to leave.


> Python Scapy does not natively support the `myTunnel` header type so we have
> provided a file called `myTunnel_header.py` which adds support to Scapy for
> our new custom header. Feel free to inspect this file if you are interested
> in learning how to do this.

#### Cleaning up environment


Use the following command to clean up all environment:

```bash
stop-net
```
