#!/bin/bash

# SCRIPT_UUID = SC202405201535400128266a6

# 定义一个函数来获取分区的大小
get_partition_size() {
    lsblk | grep "$1" | awk '{print $4}'
}



if [ `lsblk | grep "vda"  | wc -l` -eq  0 ]
   then 
      sda1_size=$(get_partition_size "sda1")
      sda2_size=$(get_partition_size "sda2")
      sda4_size=$(get_partition_size "sda4")

     # 使用条件判断语句
     if [[ $sda1_size == "512M" && $sda2_size == "64G" && $sda4_size == "64M" ]]; then
         echo "OK"
     else
         echo "FALSE"
         exit 1
     fi      
else
    vda1_size=$(get_partition_size "vda1")
    vda2_size=$(get_partition_size "vda2") 
    vda4_size=$(get_partition_size "vda4")	
	# 使用条件判断语句
    if [[ $sda1_size == "512M" && $sda2_size == "64G" && $sda4_size == "64M" ]]; then
       echo "OK"
    else
       echo "FALSE"
       exit 1
    fi
fi