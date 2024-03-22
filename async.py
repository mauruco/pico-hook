import pico_wifi.wifi as wifi

# wifi
wifi.connect()

eventType2 = {}

# class EchoServerProtocol(asyncio.DatagramProtocol):
#   def connection_made(self, transport):
#     self.transport = transport

#   def datagram_received(self, data, addr):
#     # time
#     now = time.time()
#     print(f"Received {data[16]} from {addr}")
#     ip, port = addr
#     if data[16] == 2: # controller data
#       eventType2[str(ip)+':'+str(port)] = {'addr': addr, 'timestamp': now}
#     # self.transport.sendto(data, addr)

# async def send_data(transport):
#   while True:
#     # time
#     now = time.time()
#     clientsList = list(eventType2.keys())
#     for client in clientsList:
#       data0 = make_response.makeDataResponse(0, 0, 0, 0, 0, 0)
#       transport.sendto(data0, eventType2[client]['addr'])
#       # if now - eventType2[client]['timestamp'] > 5:
#       #   print('client', client, 'timeout')
#       #   eventType2.pop(client)
#     await asyncio.sleep(1)  # Sleep for a bit to simulate sending data

# async def main():
#     print("Starting UDP server")

#     loop = asyncio.get_running_loop()

#     transport, protocol = await loop.create_datagram_endpoint(
#         lambda: EchoServerProtocol(),
#         local_addr=('0.0.0.0', 26760))

#     # Create a separate task for sending data
#     loop.create_task(send_data(transport))

#     try:
#         await asyncio.sleep(3600)  # Serve for 1 hour.
#     finally:
#         transport.close()

# asyncio.run(main())

import usocket
import uselect
import uasyncio

polltimeout = 1
max_packet = 1024
sock = None

# def close():
#     global sock
#     sock.close()

async def serve(cb, host, port, backlog=5):
    global sock
    ai = usocket.getaddrinfo(host, port)[0]  # blocking!
    s = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
    sock = s
    s.setblocking(False)
    s.bind(ai[-1])

    p = uselect.poll()
    p.register(s, uselect.POLLIN)
    to = polltimeout
    while True:
        try:
            if p.poll(to):
                buf, addr = s.recvfrom(max_packet)
                ret = cb(buf, addr)
                await uasyncio.sleep(0)
                if ret:
                    s.sendto(ret, addr)  # blocking
            await uasyncio.sleep(0)
        except uasyncio.CancelledError:
            # Shutdown server
            s.close()
            return

# Define a callback function
def cb(data, addr):
    print(f"Received {data[16]} from {addr}")
    return b"Thanks for the data!"  # Send this back

# Start the server
uasyncio.run(serve(cb, '0.0.0.0', 26760))