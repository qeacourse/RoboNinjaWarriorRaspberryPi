#!/bin/bash

USB=`lsusb | grep 2108:780b`
if [[ ! -z $USB ]]
then
	sudo modprobe usbserial vendor=0x2108 product=0x780B
else
	sudo modprobe usbserial vendor=0x2108 product=0x780C
fi
