#!/bin/bash

# SCRIPT_UUID = SC2024052820263801eba7010

if [ `lsblk |grep -v "sda\|sr0"|grep sd*|wc -l` -eq 0 ]
then
        echo "The disk is not mounted. Please check."
        exit 1
fi

mkfs.ext4 -F /dev/nvme0n1
if [ ! -d "/data" ]
then
    mkdir -p /data
fi
mount /dev/nvme0n1 /data
uuid=`blkid /dev/nvme0n1|grep -oP '(?<=UUID=")[^"]+'`
echo "UUID=$uuid /data               ext4     defaults        0 0">>/etc/fstab

mkdir -p /data/redis
mkdir -p /data/codis
