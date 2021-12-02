# Implementing Simple Forwarding

## Introduction

In this exercise, the switch must perform the following actions
for every packet:

1. forward the ipv4 packet
1. send ARP reply packet no matter the dst host is exist or not
1. send ICMP reply packet no matter the dst host is exist or not

Your will need to finish parser/deparser in SwitchIngress pipeline and 
also the logic to generate ARP/ICMP reply packet. Also you need to 
populate static flow entry to make it work.

Our P4 program will be written for the TNA architecture implemented
on Intel Tofino model software switch. The architecture file for the TNA
can be found at: lab/share/tna.p4. This file desribes the interfaces of 
the P4 programmable elements in the architecture, the supported externs,
as well as the architecture's standard metadata fields. We encourage you to take a look at it.

> **Spoiler alert:** There is a reference solution in the `solution`
> sub-directory. Feel free to compare your implementation to the
> reference.

## Step 1: Implement port forwarding

The `simple_forward.p4` file contains a skeleton P4 program with key pieces of
logic replaced by `TODO` comments. Your implementation should follow
the structure given in this file---replace each `TODO` with logic
implementing the missing piece.

A complete `simple_forward.p4` will contain the following components:

1. **TODO:** Finish header for ARP, ICMP header and packet header stack
1. **TODO:** Parsers for ARP and ICMP
2. An action to send_arp_reply() and send_icmp_echo_reply().
3. **TODO:** An const entry in table forward_or_respond

## Step 2: Run your solution

Before run solution, make sure you have a clean environment. If not please execute `stop-net` and `start-net` again.
In this lab we only need use switch1(sw1) for target.

1. In your shell, run p4c to compile p4 program:

   ```bash
   p4c -n simple_forward
   ```

   This will compile `simple_forward.p4` and generated output file in `./tofino` directory.

2. Due stratum support many device configuration, we should generate the protobuf based format binary. Run tofino.sh to build dev_config.pb.bin:

   ```bash
   tofino.sh -c ./tofino/simple_forward/simple_forward.conf
   ```

   This will generate device_config.pb.bin is current directory.

3. In new shell, execute `attach-host sw1` and add IP address to `veth7`
   ```bash
   ip addr add 192.168.1.1/24 dev veth7
   ```
   
4. In sw1, ping the other address in same network(eg. 192.168.1.100)

   ```bash
   ping 192.168.1.100
   ```

   This will send ARP to request MAC address. In this step, you should fail to get MAC due did not add flow entry to nexthop table.

5. Add flow entry to nexthop table

   ```bash
   P4Runtime sh >>> te =table_entry["SwitchIngress.nexthop"](action="send")
   P4Runtime sh >>> te.match["nh_id"]="0"
   field_id: 1
   exact {
     value: "\000"
   }
   P4Runtime sh >>> te.action["port"]="10"
   param_id: 1
   value: "\010"
   P4Runtime sh >>> te.insert
   P4Runtime sh >>> table_entry["SwitchIngress.nexthop"].read(lambda te:print(te))
   table_id: 47095512 ("SwitchIngress.nexthop")
   match {
     field_id: 1 ("nh_id")
     exact {
       value: "\\x00\\x00"
     }
   }
   action {
     action {
       action_id: 26568485 ("SwitchIngress.send")
       params {
         param_id: 1 ("port")
         value: "\\x00\\x08"
       }
     }
   }
   ```
   
   After this step, the ping to 192.168.1.100 should get MAC address of 192.168.1.100 and ICMP reply.

#### Cleaning up Environment

Use the following command to clean up all environment:

```bash
stop-net
```

