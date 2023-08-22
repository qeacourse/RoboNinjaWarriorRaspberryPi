#!/bin/bash

echo "Make sure to run this as root (no sudo)"

echo "blacklist cdc_acm" >> /etc/modprobe.d/blacklist.conf

wpa_passphrase $1 $2 >> /etc/wpa_supplicant/wpa_supplicant.conf

# make sure i2c is configured
echo "i2c-dev" >> /etc/modules
echo "dtparam=i2c_arm=on" >> /boot/config.txt

# setup camera
echo "start_x=1" >> /boot/config.txt
echo "gpu_mem=128" >> /boot/config.txt

# copy other setup files
cp rc.local /etc/rc.local
cp interfaces /etc/network/interfaces

pip3 install adafruit-circuitpython-charlcd
chmod u+s /usr/bin/tcpdump


echo "You will need to reboot before connecting to the robot"
