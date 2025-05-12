#!/bin/bash

# SCRIPT_UUID = SC202405201604560166940fc

systemctl stop salt-minion
# 定义你的master机器和minion
salt="10.166.24.3"
host=$(hostname)
USERNAME="root"
PASSWORD="9vbWL5Zk"

echo ${host}
# 检查sshpass是否已经安装
if ! command -v sshpass &> /dev/null
then
    echo "sshpass 没有安装，正在安装..."
    sudo yum -y install sshpass
else
    echo "sshpass 已经安装"
fi

# 使用ssh登录到salt master机器
#sshpass -p ${PASSWORD} ssh -t ${USERNAME}@${salt} << EOF
sshpass -p ${PASSWORD} ssh -o StrictHostKeyChecking=no ${USERNAME}@$salt << EOF
# 在salt master机器上执行salt-key命令删除minion的key
sudo salt-key -d ${host} -y

# 使用grep命令检查指定的Salt Minion是否还存在
if salt-key -L | grep ${host}; then
  echo "${host} 仍然存在"
else
  echo "成功：${host} 已经不存在"
fi

EOF

