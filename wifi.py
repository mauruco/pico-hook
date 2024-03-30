import network
from time import sleep
import network
import ubinascii
 
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

def connect(ssid, password):
  # Connect to WLAN
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  wlan.connect(ssid, password)
  print('Connecting to', ssid)
  while wlan.isconnected() == False:
      print('Waiting for connection...')
      sleep(1)

  mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
  print(mac)
  print(wlan.ifconfig())
  parts = mac.split(":")
  mac_bytearray = bytearray(int(part, 16) for part in parts)
  return wlan.ifconfig()[0], mac_bytearray
