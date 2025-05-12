

# SCRIPT_UUID = SC2024052014402401dedeec7

if [ `dmidecode |grep  -A 1 'Max Power Capacity' |grep Status|grep "OK"|wc -l` -lt 2 ]
then
        echo "The  system power supply number is less than 2,Please check"
        exit 1
fi