#!/bin/bash

# SCRIPT_UUID = SC2024052015363201d369230


systemctl restart salt-minion  && systemctl restart consul_agent && systemctl enable salt-minion && systemctl enable consul_agent

if [ `systemctl status node_exporter |sed -n 3p|awk '{print $2}'` = active ]&&[ `systemctl status salt-minion |sed -n 3p|awk '{print $2}'` = active ]&&[ `systemctl status consul_agent |sed -n 3p|awk '{print $2}'` = active ]
then
    echo "OK"
else
    echo "FALSE"
    exit 1
fi