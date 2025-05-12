#!/bin/bash 

# SCRIPT_UUID = SC2024052015305301e144480

# 重新读取主机名，重启salt-minion
rm -f /etc/salt/minion_id /etc/salt/pki/minion/*
systemctl restart salt-minion

sleep 2

# 重启consul agent
IPADDR=$(ip addr show bond0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1)
echo $IPADDR
# 定义service文件的路径
SERVICE_FILE="/usr/lib/systemd/system/consul_agent.service"

# 使用sed命令替换文件中的IP地址
sudo sed -i "s|-bind=[0-9\.]* |-bind=$IPADDR |" $SERVICE_FILE

systemctl daemon-reload
systemctl restart consul_agent

curl -s -L 'http://10.166.24.108:8001/agent/download?k=5805bacb60a1162cfc5b8ce32ddc1054a20131a4&group=1&protocol=0&root=true&runAccount=root&userAdd=false&app=0&container=0' | bash