#!/usr/bin/env python3

import subprocess
import time 
import json 

def scan_bluetooth():
	print("on")
	result = subprocess.run(["bluetoothctl","scan","on"], capture_output=True, text=True) 
	time.sleep(2)
	print("halverwegen")
	subprocess.run(["bluetoothctl","scan","off"], capture_output=True, text=True)
	print("off")

scan_bluetooth()
