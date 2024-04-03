import network
import socket
import ure
import ubinascii
from config import CONFIG

class ACCESSPOINT:
  def __init__(self):
    self.config = CONFIG()

  # helper
  def decode_latin1(self, data):
    # Create a mapping table for latin1 characters
    latin1_map = {i: chr(i) for i in range(256)}
    # Convert the bytes to a latin1 string
    return ''.join(latin1_map[b] for b in data)

  def page(self):
    # read config
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
  <form method="get">
    <h2>Last IP: {wifiIp}</h2><br>
    <p>
      <h2>Connect to a WiFi Network</h2>
      <label for="wifiSsid">SSID:</label><br>
      <input type="text" id="wifiSsid" name="wifiSsid" value="{wifiSSid}" required><br>
      <label for="wifiPassword">PASS:</label><br>
      <input type="text" id="wifiPassword" name="wifiPassword" value="{wifiPassword}" required><br>
      <br>
    </p>
    <p>
      <h2>Accelerometer and Gyroscope</h2>
      <label for="accelsensitiverange">Accel Sensitive Range:</label><br>
      <input type="number" id="accelSensitiveRange" name="accelSensitiveRange" min="0" max="3" value="{accelSensitiveRange}"><br>
      <ul>
        <li>0: +/- 2g 16384 LSB/g</li>
        <li>1: +/- 4g 8192 LSB/g</li>
        <li>2: +/- 8g 4096 LSB/g (DEFAULT)</li>
        <li>3: +/- 16g 2048 LSB/g</li>
      </ul>
      <br>
      <label for="gyrosensitiverange">Gyro Sensitive Range:</label><br>
      <input type="number" id="gyroSensitiveRange" name="gyroSensitiveRange" min="0" max="3" value="{gyroSensitiveRange}"><br>
      <ul>
        <li>0: +/- 250 °/s 131 LSB/°/s</li>
        <li>1: +/- 500 °/s 65.5 LSB/°/s</li>
        <li>2: +/- 1000 °/s 32.8 LSB/°/s (DEFAULT)</li>
        <li>3: +/- 2000 °/s 16.4 LSB/°/s</li>
      </ul>
      <br>
      <br>
    </p>
    <p>
      <h2>Hook Configuration</h2>
      <label for="serverid">Server ID:</label><br>
      <input type="number" id="serverId" name="serverId" min="1" max="255" value="{serverId}"><br>
      <label for="activeslot">Active Slot:</label><br>
      <input type="number" id="activeSlot" name="activeSlot" min="0" max="3" value="{activeSlot}"><br>
      <br>
    </p>
    <p>
      <h2>DANGER: Force Calibration</h2>
      <label for="calibrate">Do Calibration:</label><br>
      <input type="checkbox" id="forceCalibration" name="forceCalibration" checked="checked"><br>
      <br>
    </p>
    <button type="submit" id="submit">Submit</button><br>
    <script>
      const form = document.querySelector('form');
      form.addEventListener('submit', function(event) {{
        event.preventDefault();
        wifiSSid = btoa(document.getElementById("wifiSsid").value);
        wifiPassword = btoa(document.getElementById("wifiPassword").value);
        accelSensitiveRange = document.getElementById("accelSensitiveRange").value;
        gyroSensitiveRange = document.getElementById("gyroSensitiveRange").value;
        serverId = document.getElementById("serverId").value;
        activeSlot = document.getElementById("activeSlot").value;
        forceCalibration = document.getElementById("forceCalibration").checked;
        fetch(`192.168.4.1?data=${{wifiSSid}},${{wifiPassword}},${{accelSensitiveRange}},${{gyroSensitiveRange}},${{serverId}},${{activeSlot}},${{forceCalibration}}`)
        .catch(error => console.error('Error:', error));
      }});
    </script>
  </body>
</html>"""
    return html
  
  def updateConfig(self, request):
    # Find the data parameter
    match = ure.search('data=([^ ]*) ', request)
    if match:
      data = match.group(1).split(',')
      print(data)
      # wifiSsid
      wifiSSid = ubinascii.a2b_base64(data[0])
      wifiSSid = self.decode_latin1(wifiSSid)
      # wifiPassword
      wifiPassword = ubinascii.a2b_base64(data[1])
      wifiPassword = self.decode_latin1(wifiPassword)
      # accelSensitiveRange
      accelSensitiveRange = int(data[2])
      # gyroSensitiveRange
      gyroSensitiveRange = int(data[3])
      # serverId
      serverId = int(data[4])
      # activeSlot
      activeSlot = int(data[5])
      # forceCalibration
      forceCalibration = False
      if (len(data) > 6 and data[6] == 'true'):
        forceCalibration = True

      self.config.set('wifiSsid', wifiSSid)
      self.config.set('wifiPassword', wifiPassword)
      self.config.set('accelSensitiveRange', accelSensitiveRange)
      self.config.set('gyroSensitiveRange', gyroSensitiveRange)
      self.config.set('serverId', serverId)
      self.config.set('activeSlot', activeSlot)
      self.config.set('forceCalibration', 1 if forceCalibration else 0)
      self.config.save()

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
      request = str(request)
      # if has data
      self.updateConfig(request)
      conn.send(self.page()) # max 6400 caracteres
      conn.close()
