PROGRAM_NAME = basic
TARGET = sw1

all: run

run: build start
	sleep 5
	p4rt-shell -n $(TARGET) -i ./tofino/$(PROGRAM_NAME)/p4info.txt -b ./device_config.pb.bin

start:
	start-net

stop:
	stop-net

build:
	p4c -n $(PROGRAM_NAME)
	tofino.sh -c ./tofino/$(PROGRAM_NAME)/$(PROGRAM_NAME).conf

clean:
	sudo rm -rf tofino
	sudo rm device_config.pb.bin