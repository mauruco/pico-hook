import network
import socket
from config import CONFIG

class ACCESSPOINT:
  def __init__(self):
    self.config = CONFIG()

  def page(self):
    # read config
    self.config.reload()
    wifiSSid = self.config.get('wifiSsid')
    wifiPassword = self.config.get('wifiPassword')
    wifiIp = self.config.get('wifiIp')
    accelSensitiveRange = self.config.get('accelSensitiveRange')
    gyroSensitiveRange = self.config.get('gyroSensitiveRange')
    serverId = self.config.get('serverId')
    activeSlot = self.config.get('activeSlot')

    # max 6400 caracteres
    html = f"""<html>
  <head>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  </head>
  <body>
  <h1>PICO-HOOK</h1>
  <form method="post" enctype="multipart/form-data">
    <h2>Last IP: {wifiIp}</h2><br>
    <h2>Connect to a WiFi Network</h2><br>
    <p>
      <label for="ssid">SSID:</label><br>
      <input type="text" id="ssid" name="ssid" value="{wifiSSid}" required>
    </p>
    <p>
      <label for="pass">PASS:</label><br>
      <input type="password" id="pass" name="pass" value="{wifiPassword}" required>
    </p>
    <h2>Accelerometer and Gyroscope</h2><br>
    <p>
      <label for="accelsensitiverange">Accel Sensitive Range:</label><br>
      <input type="number" id="myNumber" name="myNumber" min="0" max="3" value="{accelSensitiveRange}">
      <ul>
        <li>0: +/- 2g 16384 LSB/g</li>
        <li>1: +/- 4g 8192 LSB/g</li>
        <li>2: +/- 8g 4096 LSB/g (DEFAULT)</li>
        <li>3: +/- 16g 2048 LSB/g</li>
      </ul>
      <label for="gyrosensitiverange">Gyro Sensitive Range:</label><br>
      <input type="number" id="myNumber" name="myNumber" min="0" max="3" value="{gyroSensitiveRange}">
      <ul>
        <li>0: +/- 250 °/s 131 LSB/°/s</li>
        <li>1: +/- 500 °/s 65.5 LSB/°/s</li>
        <li>2: +/- 1000 °/s 32.8 LSB/°/s (DEFAULT)</li>
        <li>3: +/- 2000 °/s 16.4 LSB/°/s</li>
      </ul>
    </p>
    <h2>Hook Configuration</h2><br>
    <p>
      <label for="serverid">Server ID:</label><br>
      <input type="number" id="myNumber" name="myNumber" min="1" max="255" value="{serverId}">
      <label for="activeslot">Active Slot:</label><br>
      <input type="number" id="myNumber" name="myNumber" min="0" max="3" value="{activeSlot}">
    </p>
    <h2>DANGER: Force Calibration</h2><br>
    <p>
      <label for="calibrate">Do Calibration:</label><br>
      <input type="checkbox" id="calibrate" name="calibrate">
    </p>
    <button type="submit">Submit</button>
  </body>
</html>"""
    return html

  def app_mode(self, ssid, password):
    # Start the Access Point
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    # IP configuration
    ap.active(True)
    # ap.ifconfig(('192.168.77.1', '255.255.255.0', '192.168.77.1', '0.0.0.0')) # does not work
    
    while ap.active() == False:
      pass
    
    print('PICO Is Now In Access Point Mode')
    print('IP Address To Connect to:: ' + ap.ifconfig()[0])
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #creating socket object
    s.bind(('', 80))
    s.listen(5)

    while True:
      conn, addr = s.accept()
      print('Got a connection from %s' % str(addr))
      request = conn.recv(1024)
      print('Content = %s' % str(request))
      conn.send(self.page()) # max 6400 caracteres
      conn.close()
      
ACCESSPOINT().app_mode('pico-hook', 'pico-hook')