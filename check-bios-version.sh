

# SCRIPT_UUID = SC202405201443410108f8078

if [ `dmidecode -t bios|grep Version|awk '{print $2}'` != "1.71" ]
then
	echo "The version of bios  is not equal,Please check"
	exit 1
fi