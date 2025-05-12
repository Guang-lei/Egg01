
# SCRIPT_UUID = SC20240520153139010610613

host=$(hostname -f)
dnsHostname=${host%%.*}
echo ${host}
echo ${dnsHostname}


zhuji_cunzai=`curl   --location --request GET "http://cmdb.pd.ximalaya.local/cmdb-web/machineManage/provider/machineInfo?name=$host"  |grep -o "$host" |wc -l`

echo $zhuji_cunzai

if [ "$zhuji_cunzai"  == "0" ];then

		# 获取eth0网卡的ip地址
		ipaddr=$(/usr/sbin/ifconfig bond0 | grep 'inet ' | awk '{print $2}' | cut -d':' -f2)

		# 打印结果
		echo "新上线机器"
		echo "需要添加DNS记录的主机名为$host,IP地址为${ipaddr}"

		# 通过内网调用
		url="http://cmdb.pd.ximalaya.local/cmdb-web/api/v1/dns/provider/record/add"
		token="8b1e6a47-0f29-481c-8f55-30eaafff3ebc"
		contentType="application/json"
		data="{
			\"env\": \"product\",
			\"domainId\": 127,
			\"name\": \"${dnsHostname}\",
			\"type\": \"A\",
			\"value\": \"${ipaddr}\",
			\"ttl\": 60,
			\"monitor\": 1
		}"

		# 执行 curl 命令
		curl --location "$url" \
		--header "Token: $token" \
		--header "Content-Type: $contentType" \
		--data "$data"

else
		
		echo "非首次上线机器,重新启用DNS"
		message=$(curl --location "http://cmdb.pd.ximalaya.local/cmdb-web/api/v1/dns/provider/sub/domain/list?env=product&name=$host" \
		--header 'Token: 8b1e6a47-0f29-481c-8f55-30eaafff3ebc')
		#echo ${message}

		ID=$(echo $message | awk -F ',' '{print $3}'|awk -F ':' '{print $3}')

		echo ${ID}

		curl --location 'http://cmdb.pd.ximalaya.local/cmdb-web/api/v1/dns/provider/record/status' \
		--header 'Token: 8b1e6a47-0f29-481c-8f55-30eaafff3ebc' \
		--header 'Content-Type: application/json' \
		--data '{
			"id":'$ID',
			"status":"ENABLE"
		}'
fi