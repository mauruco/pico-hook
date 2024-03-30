import ustruct
import utime

class CEMU:
  def __init__(self):
    self.packetNumber = 0

  def calculate_crc32(self, data):
      crc = 0xffffffff
      for byte in data:
          crc ^= byte
          for _ in range(8):
              if crc & 1:
                  crc = (crc >> 1) ^ 0xEDB88320
              else:
                  crc >>= 1
      return crc ^ 0xffffffff

  def make_info_response(self, mac, serverId, activeSlot, slot):
      output = bytearray(32)  # 0x0 as default
      # shared between info and data ->
      # Magic server string (DSUS)
      output[0] = 0x44
      output[1] = 0x53
      output[2] = 0x55
      output[3] = 0x53
      # Protocol version (1001)
      ustruct.pack_into('<H', output, 4, 0xE9)
      ustruct.pack_into('<H', output, 5, 0x03)
      # Packet length without header plus the length of event type (16)
      ustruct.pack_into('<H', output, 6, 16)
      # Zero out CRC32 field
      ustruct.pack_into('<L', output, 8, 0)
      # Set server id to some value (0)
      ustruct.pack_into('<L', output, 12, serverId)
      # Event type, controller information (0x00100001)
      ustruct.pack_into('<L', output, 16, 0x00100001)

      # Slot of the device we are reporting about (i)
      output[20] = slot
      # output[21] = 0x00  # Slot state, not connected (0)
      # output[22] = 0x00  # Device model, not applicable (0)
      # output[23] = 0x00  # Connection type, not applicable (0)
      # 24, 29 -> MAC address of device
      output[24:30] = mac
      # Battery status, not applicable (0)
      # output[30] = 0x00

      # # Controller 0 is the only active controller
      if slot == activeSlot:
        output[21] = 0x02  # Slot state, connected (2)
        output[22] = 0x02  # Device model, full gyro aka DS4 (2)
        output[23] = 0x02  # Connection type, bluetooth (2). (May be either USB (1) or Bluetooth (2))
        # MAC address of device (0x000000000001)
        output[24] = 0x01
        # Battery status, full (5)
        output[30] = 0x05
      ## <- shared between info and data
      
      # 31 Termination byte
      # output[31] = 0x00

      # Calculate CRC32 and write it into the output
      # Note: You'll need to implement or import a function to calculate CRC32
      crc = self.calculate_crc32(output)
      ustruct.pack_into('<L', output, 8, crc)
      return output

  def make_data_response(self, mac, serverId, activeSlot, ax, ay, az, pitch, roll, yaw):
      output = bytearray(100)  # already 0x0 as default
      ## shared between info and data ->
      # Magic server string (DSUS)
      output[0:4] = b'DSUS'  # 0:4 means 0, 1, 2, 3 ant not including output[4]
      # Protocol version (1001)
      output[4:6] = b'\xE9\x03'
      # Packet length without header plus the length of event type (4)
      ustruct.pack_into('<H', output, 6, 84)
      # Zero out CRC32 field
      ustruct.pack_into('<L', output, 8, 0)
      # Set server id to some value (0)
      ustruct.pack_into('<L', output, 12, serverId)
      # Event type, controller data (0x00100002)
      ustruct.pack_into('<L', output, 16, 0x00100002)
      # active slot
      output[20] = activeSlot
      # slot state
      output[21] = 0x02
      # device model
      output[22] = 0x02
      # connection type
      output[23] = 0x02
      # 24, 29 -> MAC address of device
      output[24:30] = mac
      # battery status
      output[30] = 0x05
      ## <- shared between info and data

      # device active
      output[31] = 0x01
      # Copy from packetCount to packet array 
      ustruct.pack_into('<L', output, 32, self.packetNumber)
      self.packetNumber += 1
      # We don't care about button, joystick and touchpad data, so we just their bytes to zero.
      # output[36:68] = b'\x00' * 32
      # timestamp
      # micro time passed
      ustruct.pack_into('<Q', output, 68, utime.ticks_us() & 0xFFFFFFFFFFFF)
      # -- gyro shake
      # Acceleration X
      ustruct.pack_into('<f', output, 76, ax)
      # Acceleration Y
      ustruct.pack_into('<f', output, 80, ay)
      # Acceleration Z
      ustruct.pack_into('<f', output, 84, az)
      # Gyroscope Pitch
      ustruct.pack_into('<f', output, 88, pitch)
      # Gyroscope Yaw
      ustruct.pack_into('<f', output, 92, yaw)
      # Gyroscope Roll
      ustruct.pack_into('<f', output, 96, roll)

      # Calculate CRC32 and write it into the output
      # Note: You'll need to implement or import a function to calculate CRC32
      crc = self.calculate_crc32(output)
      ustruct.pack_into('<L', output, 8, crc)
      return output