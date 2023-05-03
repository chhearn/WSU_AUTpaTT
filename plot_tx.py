#!/usr/bin/python

import math
import matplotlib.pyplot as plt
from pprint import pprint


# read in data file
mast_angles = []
arm_angles = []
rssi = []
fp = open("antenna_data.txt", 'r')
for line in fp:
    if line[0] == '%' or line[0].strip() == '':
        continue # skip comment lines and empty lines
    mast_angle,arm_angle,background_rssi,transmit_rssi = line.split(',')
    mast_angles.append(float(mast_angle))
    arm_angles.append(float(arm_angle))
    rssi.append(float(transmit_rssi))
fp.close()

# adjust angle data to 0-360 degree range
#min_angle = mast_angles.

# plot the data
ax = plt.subplot(111, projection='polar')
theta = [angle*(math.pi/180) for angle in mast_angles]
ax.plot(theta, rssi)
ax.set_rmax(50)
ax.set_rticks([0, 10, 20, 30, 40])
ax.set_rlabel_position(-22.5)
ax.grid(True)
ax.set_title("Measured Uncorrected RSSI Pattern of a Yagi Antenna", va="bottom")
plt.show()

