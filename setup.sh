#!/bin/bash

# TODO: add install of tcpdump, starting of video-manager, enabling camera, and setting suid on tcpdump
echo "Make sure to run this as root (no sudo)"

echo "blacklist cdc_acm" >> /etc/modprobe.d/blacklist.conf

# configure wifi via wpa_supplicant
echo "enter SSID:"
read SSID

echo "enter SSID key:"
read PSK

wpa_passphrase $SSID $PSK >> /etc/wpa_supplicant/wpa_supplicant.conf

# make sure i2c is configured
echo "i2c-dev" >> /etc/modules
echo "dtparam=i2c_arm=on" >> /boot/config.txt

# setup camera
echo "start_x=1" >> /boot/config.txt
echo "gpu_mem=128" >> /boot/config.txt

# install python libraries that are no longer available via standard installation methods
cp -r dist-packages/* /usr/local/lib/python2.7/dist-packages

# copy other setup files
cp rc.local /etc/rc.local
cp interfaces /etc/network/interfaces

# install wifi drivers (if custom versino needed)
wget http://downloads.fars-robotics.net/wifi-drivers/install-wifi -O /usr/bin/install-wifi
chmod +x /usr/bin/install-wifi
install-wifi

echo "You will need to reboot before connecting to the robot"
