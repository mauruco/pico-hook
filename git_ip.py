from os import stat
from sys import exit
from wifi import connect
from json import loads

# helper
def file_exists(filename):
  try:
    stat(filename)
    return True
  except OSError:
    return False
  
# wifi
if not file_exists('config.json'):
  print('config.json not found')
  exit()

wifiConfig = {}
with open('config.json', 'r') as f:
  wifiConfig = loads(f.read())

# print ip
ip = connect(wifiConfig['wifiSsid'], wifiConfig['wifiPass'])