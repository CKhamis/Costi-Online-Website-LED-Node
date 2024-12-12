# Connect to network
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Birdie - SH', 'JJCAAKhamis')

# Make GET request
import urequests
import ujson
import utime

while True:
    r = urequests.get("http://www.costionline.com/api/v1/Media/analytics")
    parsed_response = ujson.loads(r.content)
    r.close()
    print(parsed_response['youtubeCount'])
    utime.sleep(5)
    