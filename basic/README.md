# Implementing Basic Forwarding

## Introduction

The objective of this exercise is to write a P4 program that
implements basic forwarding. To keep things simple, we will just
implement forwarding by port.

With IPv4 forwarding, the switch must perform the following actions
for every packet:

1. forward the packet out the appropriate port.

Your switch will have a single table, which you will need to populate flow rules.
Each rule will map an ingress port for the next hop. You will need to implement 
the data plane logic of your P4 program.

Our P4 program will be written for the TNA architecture implemented
on Intel Tofino model software switch. The architecture file for the TNA
can be found at: lab/share/tna.p4. This file desribes the interfaces of 
the P4 programmable elements in the architecture, the supported externs,
as well as the architecture's standard metadata fields. We encourage you to take a look at it.

> **Spoiler alert:** There is a reference solution in the `solution`
> sub-directory. Feel free to compare your implementation to the
> reference.

## Step 1: Implement port forwarding

The `basic.p4` file contains a skeleton P4 program with key pieces of
logic replaced by `TODO` comments. Your implementation should follow
the structure given in this file---replace each `TODO` with logic
implementing the missing piece.

A complete `basic.p4` will contain the following components:

1. **TODO:** Parsers for Ethernet and IPv4 that populate `ethernet_t` and `ipv4_t` fields.
2. An action to drop a packet, using `the metadata in ingress_intrinsic_metadata_for_deparser_t`.
3. **TODO:** An action (called `forward`) that:
  1. Sets the egress port for the next hop. 
4. **TODO:** A control that:
    1. Defines a table that will read an IPv4 destination address, and
       invoke either `drop` or `forward`.
    2. An `apply` block that applies the table.   
5. **TODO:** A deparser that selects the order
    in which fields inserted into the outgoing packet.
6. A `package` instantiation supplied with the parser, control, and deparser.

## Step 2: Run your solution

Before run solution, make sure you have a clean environment. If not please execute `stop-net` and `start-net` again.
In this lab we only need use switch1(sw1) for target.

1. In your shell, run p4c to compile p4 program:

   ```bash
   p4c -n basic
   ```

   This will compile `basic.p4` and generated output file in `./tofino` directory.

2. Due stratum support many device configuration, we should generate the protobuf based format binary. Run tofino.sh to build dev_config.pb.bin:

   ```bash
   tofino.sh -c ./tofino/basic/basic.conf
   ```

   This will generate device_config.pb.bin is current directory.

3. Run p4runtime-shell to load pipeline and add flow entries:

   ```bash
   p4rt-shell -n sw1 -i ./tofino/basic/p4info.txt -b ./device_config.pb.bin
   P4Runtime sh >>> te = table_entry["SwitchIngress.forward"](action="SwitchIngress.hit")
   P4Runtime sh >>> te.match["ig_intr_md.ingress_port"]="3"
   P4Runtime sh >>> te.action["port"]="4"
   P4Runtime sh >>> te.insert
   P4Runtime sh >>> table_entry["SwitchIngress.forward"].read(lambda te: print(te))
   table_id: 37882547 ("SwitchIngress.forward")
   match {
     field_id: 1 ("ig_intr_md.ingress_port")
     exact {
       value: "\\x00\\x03"
     }
   }
   action {
     action {
       action_id: 32848556 ("SwitchIngress.hit")
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
   ```

5. In new shell, execute `attach-host sw1` and run receive.py

   ```bash
   python receive.py
   ```

   This will listen packets on port 4

6. In other new shell, execute `attach-host sw1` and run send.py with destination IP and message

   ```bash
   python send.py <destination IP> "<MESSAGE>"
   ```

   This will send packet to port 3 and you should see packet content in shell which execute `receive.py`

#### Cleaning up Environment

Use the following command to clean up all environment:

```bash
stop-net
```

