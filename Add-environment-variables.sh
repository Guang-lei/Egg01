

# SCRIPT_UUID = SC20240520153805010c1ee49


CPUNUM=`nproc`
MEM=`free -g|sed -n 2p|awk '{print $2}'`
IP=`ifconfig bond0|sed -n 2p|awk '{print $2}'`
REGION=`hostname|awk -F '-' '{print $1}'|tr '[:lower:]' '[:upper:]'`

AZ=`hostname|awk -F '-' '{print $2}'`
if [ $REGION = SH1 ]
  then
    lREGION=shanghai-1
else
    lREGION=beijing-4
fi

export LOCAL_REGION=$lREGION
export LOCAL_AZ=HW$REGIONAZ$AZ
export LOCAL_IP=$IP
export LOCAL_CPU=$CPUNUM
export LOCAL_MEM=$MEM
export NACOS_DOMAIN_ADDR=nacosnh.pd.ximalaya.local:80,nacosnh2.pd.ximalaya.local:80


echo "export LOCAL_REGION=$lREGION
export LOCAL_AZ=HW-$REGION-AZ$AZ
export LOCAL_IP=$IP
export LOCAL_CPU=$CPUNUM
export LOCAL_MEM=$MEM
export NACOS_DOMAIN_ADDR=nacosnh.pd.ximalaya.local:80,nacosnh2.pd.ximalaya.local:80">>/etc/profile

source /etc/profile