import network
import socket
import time
import json

# To turn on the onboard LED
# from machine import Pin
# import time
# led = Pin("LED", Pin.OUT) 
#  
# while True:
#     led.low()
#     time.sleep_ms(500)
#     led.high()
#     time.sleep_ms(500)


from machine import Pin
from neopixel import Neopixel

onboard_led = Pin("LED", Pin.OUT)

led = Pin("LED", Pin.OUT)
numpix = 900
strip = Neopixel(numpix, 0, 28, "GRB")
#red = (255, 255,255)
strip.brightness(50)
#strip.fill(red)
#strip.show()

ssid = 'Birdie - SH'
password = '????'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

#Global variables
label = ""
color = ""
pattern = ""

def parse_rgb_string(rgb_string):
    rgb_values = rgb_string.replace("rgb(", "").replace(")", "")
    r, g, b = rgb_values.split(",")
    print("Colors:")
    print("red "+ r)
    print("gren" + g)
    print("blue" + b)
    return int(r), int(g), int(b)

onboard_led.value(1)

#Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)
        
        request = b""
        while "\r\n\r\n" not in request:
            request += cl.recv(1024)
        
        #request += cl.recv(1024)
        print("Request header:")
        print(request)
        
        request = request.decode("utf-8")
        
        if request.find('POST /') != -1:
            request += str(cl.recv(1024))
            # Extract JSON data from request body
            body_start = request.find('{')
            body_end = request.find('}', body_start)
            json_data = request[body_start:body_end + 1]
            print("Request body:")
            print(json_data)
            data = json.loads(json_data)

            # Update global variables
            address = data.get('address', "")
            label = data.get('label', "")
            color = data.get('color', "")
            pattern = data.get('pattern', "")
            print(pattern)
            
            response_data = {
                "status": "success",
                "message": "Data received successfully"
            }
            
            if color.find('rgb') != -1:
                if pattern.isdigit():
                    strip.brightness(int(pattern))
                else:
                    print("Pattern could not be parsed")
                    pattern = 100
                    
                strip.fill(parse_rgb_string(color))
                strip.show()

            response_code = 'HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n'
        elif request.find('GET /') != -1:
            response_data = {
                "address": status[0],
                "label": label,
                "color": color,
                "pattern": pattern
            }
            response_code = 'HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n'
        else:
            response_data = {
                "status": "error",
                "message": "Invalid request"
            }
            response_code = 'HTTP/1.0 400 Bad Request\r\nContent-type: application/json\r\n\r\n'
        
        response_json = json.dumps(response_data)
        
        if color == "on":
            led.value(1)
        else:
            led.value(0)

        cl.send(response_code)
        cl.send(response_json)
        cl.close()

    except OSError as e:
        cl.close()
        led.value(0)
        print('connection closed')