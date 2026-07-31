import sys
import requests
from bs4 import BeautifulSoup
import re
import time
import math

def read_webpage(url):
    try:
        response = requests.get(url, timeout = 30)
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
            output_to_log(f"Error: {f}\n")
    except Exception as e:
        output_to_log(f"Error: {e}\n")

# takes depth in cm and returns gallons in tank 
def gallons_from_depth( depth ):
    # Because of the periodicity of the sin/asin functions, we need to keep the inputs normalized.
    # To do that, we normalize the depth reading and calculate what the volume of liquid would
    # be in that virtual, normalized tank with a radius of 0.5m and a length of 1.273m (to provide
    # a volume of 1 m^3).
    # Then we apply the fraction to the actual tank volume.
    realTankDepth = 2.25 # m
    realTankLength = 6.4 # m
    realTankVolume = realTankLength * math.pi * (realTankDepth/2)**2
    fracDepth = (depth/100) / realTankDepth # normalized depth (1.0 = full tank) for current depth reading

    # Calculate fractional volume for a virtual 1 m^3 tank at the current fractional Depth
    vL = 1.273 # virtual tank length, m
    vR = 0.5   # virtual tank radius, m
    virtualMaxVolume = vL * vR**2 * math.pi
    eps = 0.01
    if (virtualMaxVolume > 1+eps) or (virtualMaxVolume < 1-eps):
        raise ValueError("Virtual Tank does not have a valid volume.")

    # Note: volume calculation comes from Natalie's exact calculus solution for a cylinder laying
    # on its side. It does not include the semi-spherical end-cap volumes, so is an underestimate
    # of the total water volume.
    # 
    # This computes the virtual volume given the current fractional depth
    vV = abs(vL*vR**2*(math.asin((vR-fracDepth)/vR)-math.pi/2+0.5*math.sin(2*math.asin((vR-fracDepth)/vR))))
    fracVolume = vV / (math.pi/4.0)
    realVolume = fracVolume * realTankVolume # m
    # Convert volume into gallons
    # 1 m^3 -> 296.91 gallons
    realVolumeGal = realVolume * 296.91

    return realVolumeGal


fullPathCsvFile = r"C:\Users\mohr\Documents\Projects\rainwater_tank\data\pumpMonitorData.csv"
fullPathLogFile = r"C:\Users\mohr\Documents\Projects\rainwater_tank\data\log.txt"

def output_to_csv( outstr ):
    file_object = open(fullPathCsvFile, 'a')
    file_object.write( outstr )
    file_object.close()

def output_to_log( outstr ):
    file_object = open(fullPathLogFile, 'a')
    file_object.write( outstr )
    file_object.close()

if __name__ == "__main__":
    webpage_url = 'http://192.168.0.227'

    # assume pump controller is off to begin with
    pumpControllerOn = False
    printUpdateToConsoleInterval = 10
    updateCount = 0

    try:
        outstr = "\n\n"
        outstr = outstr + "=====================================================================================" + "\n"
        outstr = outstr + "Pump Control Monitoring Service starting at: "
        outstr = outstr + time.strftime("%d %b %Y, %H:%M:%S", time.localtime()) + "\n"
        outstr = outstr + "Data file being logged is at: " + fullPathCsvFile + "\n"
        outstr = outstr + "Console output is recorded at: " + fullPathLogFile + "\n"
        outstr = outstr + "=====================================================================================" + "\n"
        outstr = outstr + "\n"
        output_to_log(outstr)

        while True:
            result = read_webpage(webpage_url)

            if result is not None:
                if result[0] != -1:
                    tankDepth = result[0]
                else:
                    tankDepth = -1

                if result[1] != -1:
                    # PUMP CONTROLLER IS ON

                    # if this is the first reading since the pump controller was seen to be
                    # off, we need to latch the start time and reset the cumulative pump
                    # run time
                    if pumpControllerOn == False:
                        pumpControllerOn = True
                        tankDepthAtStart = tankDepth
                        timeAtStart = time.time()
                        outstr = "ON: " + time.strftime("%d %b %Y, %H:%M:%S", time.localtime()) + "\n"
                        output_to_log( outstr )

                    # update the cumulative variable (can't do this after the pump controller is off)
                    cumulativePumpRunTime = result[2]
                    
                    if updateCount % printUpdateToConsoleInterval == 0:
                        outstr = "Stream Run Time: " + str(round(time.time() - timeAtStart))
                        outstr = outstr + " Pump Run Time: " + str(cumulativePumpRunTime)
                        outstr = outstr + " Tank Depth: " + str(tankDepth)
                        outstr = outstr + " Tank Volume: " + str(round(gallons_from_depth(float(tankDepth)))) + "\n"
                        output_to_log( outstr )
                else:
                    # PUMP CONTROLLER IS OFF

                    # if this is the first reading since the pump controller was seen to be
                    # on, the change of states means we need to log the data we have
                    if pumpControllerOn == True:
                        pumpControllerOn = False
                        totalStreamRunTime = time.time() - timeAtStart
                        humanTime = time.strftime("%d %b %Y, %H:%M:%S", time.localtime())
                        outstr = humanTime + ', ' + str(round(totalStreamRunTime)) + ', ' + str(cumulativePumpRunTime) 
                        outstr = outstr + ', ' + str(tankDepthAtStart) + ', ' + str(tankDepth)
                        outstr = outstr + ', ' + str(round(gallons_from_depth(float(tankDepthAtStart))))
                        outstr = outstr + ', ' + str(round(gallons_from_depth(float(tankDepth))))
                        outstr = outstr + '\n'
                        outstrBackup = outstr
                        output_to_csv( outstr )
                        outstr = "-------------------------------------------------------------------------------------" + "\n"
                        outstr = outstr + "OFF: " + time.strftime("%d %b %Y, %H:%M:%S", time.localtime()) + "\n"
                        outstr = outstr + "DATA: " + outstrBackup + "\n"
                        outstr = outstr + "(local time, stream run time, cumulative pump run time, tank depth at start, " + "\n"
                        outstr = outstr + " ... tank depth at end, tank gallons at start, tank gallons at end)" + "\n"
                        outstr = outstr + "-------------------------------------------------------------------------------------" + "\n"
                        output_to_log( outstr )
            else:
                outstr = "Error: no response from server. " + time.strftime("%d %b %Y, %H:%M:%S", time.localtime()) + "\n"
                output_to_log( outstr )

            # Sleep for 1 minute
            time.sleep(1 * 60)
            updateCount = updateCount + 1
    except KeyboardInterrupt:
        outstr = "Exiting: Service stopped." + "\n"
        output_to_log( outstr )
        sys.exit()