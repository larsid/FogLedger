#!/bin/bash
ifconfig -a | grep -oP '^\w+'
mtu_value=5000  # Set your desired MTU value here

for interface in $(ifconfig -a | grep -oP '^\w+'); do
    ifconfig $interface mtu $mtu_value
done