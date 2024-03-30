from json import loads, dumps
from os import stat

  
class CONFIG:
  def __init__(self):
    self.filename = 'config.json'
    # default config
    self.config = {
      'wifiSsid': 'pico-hook',
      'wifiPassword': 'pico-hook',
      'wifiIp': '0.0.0.0',
      'forceCalibration': 0,
      "serverId": 1,
      "activeSlot": 0,
      "accelSensitiveRange": 2, # +/- 8g 4096 LSB/g
      "gyroSensitiveRange": 2, # +/- 1000 °/s 32.8 LSB/°/s
      "ax": 0,
      "ay": 0,
      "az": 0,
      "gx": 0,
      "gy": 0,
      "gz": 0,
    }
    
    # create config file if not exists
    if not self.file_exists(self.filename):
      with open(self.filename, 'w') as f:
        f.write(dumps(self.config))
    # load config
    else:
      with open(self.filename, 'r') as f:
        self.config = loads(f.read())

  def reload(self):
    with open(self.filename, 'r') as f:
      self.config = loads(f.read())
  
  # helper
  def file_exists(self, filename):
    try:
      stat(filename)
      return True
    except OSError:
      return False
  
  def get(self, key):
    return self.config[key]
  
  def set(self, key, value):
    self.config[key] = value

  def save(self):
    with open(self.filename, 'w') as f:
      f.write(dumps(self.config))
  
  def all(self):
    return self.config