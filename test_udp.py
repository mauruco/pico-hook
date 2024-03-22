#!/usr/bin/env python3
from machine import UART, Pin
import utime,time


# WIFI router information, please fill in your own WIFI router information
SSID='AntonioEstarque'               # WIFI name
password = '#O020898Vwifi'           # WIFI password
remote_IP = '192.168.15.10'       # Computer's IP address, needs to be changed by yourself
remote_Port = '26760'             # Computer's port number
local_Port = '26760'              # Local UDP port

# Serial port mapped to GP0 and GP1 ports, do not use GP0 and GP1 ports
# when communicating with the WIFI module
esp_uart = UART(0, 115200)   # Serial port 0, baud rate is 115200

# Function to send commands
def esp_sendCMD(cmd,ack,timeout=2000.0):
    esp_uart.write(cmd+'\r\n')
    i_t = utime.ticks_ms()
    while (utime.ticks_ms() - i_t) < timeout:
        s_get=esp_uart.read()
        if(s_get != None):
            # s_get=s_get.decode()
            print('s_get')
            print(str(s_get))
            s_get=str(s_get)
            if(s_get.find(ack) >= 0):
                return True
    return False

# Program entry point
esp_uart.write('+++')           # Initialize to exit transparent mode
time.sleep(1)
if(esp_uart.any()>0):
    esp_uart.read()
esp_sendCMD("AT","OK")          # AT command
esp_sendCMD("AT+CWMODE=3","OK") # Configure WiFi mode
esp_sendCMD("AT+CWJAP=\""+SSID+"\",\""+password+"\"","OK",20000) # Connect to the router
esp_sendCMD("AT+CIFSR","OK")                                     # Query the IP address of the WIFI module
esp_sendCMD("AT+CIPSTART=\"UDP\",\""+remote_IP+"\","+remote_Port+","+local_Port+",0","OK",10000) # Create UDP transmission
esp_sendCMD("AT+CIPMODE=0","OK")    # Enable transparent mode, data can be directly transmitted 

while True:
  s_get=esp_uart.read()
  if(s_get != None):
      # s_get=s_get.decode()
      print('s_get')
      print(str(s_get))

  time.sleep(0.01)
