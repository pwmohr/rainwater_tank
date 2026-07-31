import sys
import requests
from bs4 import BeautifulSoup
import re
import time

def read_webpage(url):
    try:
        response = requests.get(url, timeout = 16)
        try:
            depthReading = False
            floatReading = False
            returnValue = [-1, -1, -1]

            if response.status_code == 200:
                s = BeautifulSoup(response.text, 'html.parser')
                t = s.find(id='tankDepth')
                if t is not None:
                    m = re.search('[0-9]+\\.*[0-9]*', t.text)
                    depthReading = True

                p = s.find(id='pumpStatus')
                if p is not None:
                    pump = re.search('on|off', p.text)
                    floatReading = True
                
                if depthReading == True:
                    returnValue[0] = m.group(0)

                if floatReading == True:
                    returnValue[1] = pump.group(0)

                q = s.find(id='runTime')
                if q is not None:
                    runTime = re.search('[0-9]+\\.*[0-9]*', q.text)
                    returnValue[2] = runTime.group(0)

                return returnValue
            else:
                return -1
        except Exception as f:
            print(f"Error: {f}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    webpage_url = 'http://192.168.0.227'
    while True:
        file_object = open(r"C:\Users\mohr\Downloads\tankData.csv", 'a')
        result = read_webpage(webpage_url)
        humanTime = time.strftime("%d %b %Y, %H:%M:%S", time.localtime())
        machineTime = time.time()
        outString = humanTime + ', ' + str(machineTime)

        if result is not None:
            if result[0] != -1:
                outString = outString + ', ' + result[0] + ', ' + 'cm'
            else:
                outString = outString + ', ' + 'Tank Depth Offline' + ', ' + 'n/a'

            if result[1] != -1:
                outString = outString + ', ' + result[1]
            else:
                outString = outString + ', ' + 'Pump Controller Offline'

            if result[2] != -1:
                outString = outString + ', ' + result[2]
                
            outString = outString + '\n'
            print(outString)
            file_object.write(outString)

        else:
            file_object.write('Error reading feed.\n')

        file_object.close()

        # Sleep for 1 minute
        time.sleep(1 * 60)