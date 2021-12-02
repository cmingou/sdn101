# Implementing timestamp

## Introduction

In this exercise, we will add a new packet header for support timestamp. 
The p4 program should only have one table to forward packet based on ingress port and
will set timestamp into header in each stage. The software switch we are using 
is support Tofino 1 and the timestamp header format already describe in program.


> **Spoiler alert:** There is a reference solution in the `solution`
> sub-directory. Feel free to compare your implementation to the reference.

The starter code for this assignment is in a file called `timestamp.p4` and
is a simply architecture to provide timestamp function.


### A note about the control plane

A P4 program defines a packet-processing pipeline, but the rules within each
table are inserted by the control plane. When a rule matches a packet, its
action is invoked with parameters supplied by the control plane as part of the
rule.

For this exercise, you should add the necessary control plane entries. 

**Important:** We use P4Runtime shell to install the control plane rules.

## Step 1: Implement timestamp

The `timestamp.p4` file not contains any table yet.  It contains comments marked
 with `TODO` which indicate the functionality that you need to implement. 
A complete implementation of the `timestamp.p4` switch will be able to forward 
based on the ingress port.

Your job will be to do the following:

1. **TODO:** Add appropriate parser flow.
2. **TODO:** Define a new table and action to forward packet based ingress port.
3. **TODO:** Add more table and action into pipeline and obverse the change of time comsumption.

## Step 2: Run your solution

Before run solution, make sure you have a clean environment. If not please execute `stop-net` and `start-net` again.
In this lab we only need use switch1(sw1) for target.

1. In your shell, run:
   ```bash
   p4c -n timestamp
   ```
   This will compile `timestamp.p4` and generated output file in `./tofino` directory.

2. Due stratum support many device configuration, we should generate the protobuf based format binary. Run tofino.sh to build dev_config.pb.bin:

   ```bash
   tofino.sh -c ./tofino/timestamp/timestamp.conf
   ```

   This will generate device_config.pb.bin is current directory.
   
3. Run p4runtime-shell to load pipeline and add flow entries:

   ```bash
   p4rt-shell -n sw1 -i ./tofino/timestamp/p4info.txt -b ./device_config.pb.bin
   P4Runtime sh >>> te = table_entry["SwitchIngress.output_port"](action="SwitchIngress.set_output_port")
   P4Runtime sh >>> te.match["ig_intr_md.ingress_port"]="3"
   P4Runtime sh >>> te.action["port_id"]="4"
   P4Runtime sh >>> te.insert
   P4Runtime sh >>> table_entry["SwitchIngress.output_port"].read(lambda te: print(te))
   table_id: 35437855 ("SwitchIngress.output_port")
   match {
     field_id: 1 ("ig_intr_md.ingress_port")
     exact {
       value: "\\x00\\x03"
     }
   }
   action {
     action {
       action_id: 21556202 ("SwitchIngress.set_output_port")
       params {
         param_id: 1 ("port_id")
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
5. Now we in new shell, execute `attach-host sw1` and start listen packet on port 4: 
  ```bash
  python ./receive.py
  ```
  The packet should be received at `veth9`, and show 6 timestamps(`ingress mac`, `ingress global`, `traffic manager enqueue`, `traffic manager dequeue delta`, `egress global`, `egress tx`). 

6. In new shell, execute `attach-host sw1` and send a packet: 
  ```bash
  python ./send.py
  ```
8. Type `exit` to leave.

#### Cleaning up environment


Use the following command to clean up all environment:

```bash
stop-net
```
