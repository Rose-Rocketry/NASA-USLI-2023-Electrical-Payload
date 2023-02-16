import json
counter = 0
time = []
altitude = []
alt = 0
t = 0
launched = False
landed = False
with open('State Machine\mpl3115.json') as data:
    for line in data:
        set = json.loads(line)
        time.append(set["timestamp"])
        altitude.append(set["altitude"])
data.close()
for i in range(9, len(time)+1):
    if (not launched): 
        for j in range(0, 10):
            alt += altitude[i-j]
        alt = alt/10
        if alt > (altitude[0] + 500):
            print("Launch detected at " + str(time[i]) + " sec with an altitude of " + str(altitude[i]) + " meters")
            launched = True
            launchTime = time[i]
    if (not landed) and launched:
        speed = abs(altitude[i] - altitude[i-9]) / (time[i] - time[i-9])
        if speed >= 2.0:
            timeCheck = time[i]
        elif (time[i]-launchTime > 300) and (time[i]-timeCheck > 60.2):
            print("Landing detected at " + str(time[i]) + " sec with an altitude of " + str(altitude[i]) + " meters")
            landed = True
            landTime = time[i]
            break