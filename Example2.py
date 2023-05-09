# Written By: Brandon Johns
# Date Version Created: 2023-05-09
# Date Last Edited: 2023-05-09
# Status: NOT TESTED

### PURPOSE ###
# Example for using Brandon's interface to the 'OptiTrack NatNet SDK'
# Print locations of objects to the screen

### NOTES ###
# First follow the Prerequisite Setup in the readme


from NatNetPython import OTInterface as OTInterface
import time
import numpy


############################################################################################
# Startup
##############################################
# Instance the interface
ot = OTInterface.Interface(clientAddress="127.0.0.1", serverAddress="127.0.0.1")

# List all the objects to capture
#   key = The 'Streaming ID' as configured within Motive (see the readme for more information)
#   val = A friendly name to be used as the key for returned frames
ot.allowList[100] = 'Jackal'
ot.allowList[101] = 'Pedestrian'

ot.Connect()


############################################################################################
# Main loop
##############################################
timeStart = time.time()
duration = 3 # [s]

# Collect data
while time.time() - timeStart < duration:
    # Get next data frame
    frame = ot.GetFrame_GetUnread()

    print('')
    print('Frame Number [Count]:', frame.FrameNumber())
    print('Frame Age [s]:', frame.FrameAge_seconds())

    Jackal = frame.GetByName('Jackal')
    Pedestrian = frame.GetByName('Pedestrian')

    print('Jackal     (x,y,z) [mm]:', Jackal.P().transpose())
    print('Pedestrian (x,y,z) [mm]:', Pedestrian.P().transpose())

    if (not Jackal.IsOccluded()) and (not Pedestrian.IsOccluded()):
        Position_JackalRelPedestrian = Pedestrian.Inv() @ Jackal
        print('Position of Jackal, relative to Pedestrian:', Position_JackalRelPedestrian.P().transpose())

ot.Disconnect()
