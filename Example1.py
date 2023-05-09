# Written By: Brandon Johns
# Date Version Created: 2023-05-09
# Date Last Edited: 2023-05-09
# Status: NOT TESTED

### PURPOSE ###
# Example for using Brandon's interface to the 'OptiTrack NatNet SDK'
# Demonstrate use of all functions

### NOTES ###
# First follow the Prerequisite Setup in the readme


from NatNetPython import OTInterface as OTInterface


############################################################################################
# Startup
##############################################
# Instance the interface
#   These are the default addresses for use if OptiTrack Motive and this script are being run on the same machine
#   Otherwise change them
ot = OTInterface.Interface(clientAddress="127.0.0.1", serverAddress="127.0.0.1")

# List all the objects to capture
#   key = The 'Streaming ID' as configured within Motive (see the readme for more information)
#   val = A friendly name to be used as the key for returned frames
ot.allowList[100] = 'Jackal'
ot.allowList[101] = 'Pedestrian'

ot.Connect()


############################################################################################
# Get Data Frame
##############################################
# Get next data frame
frame = ot.GetFrame()

print("Frame Number [Count]", frame.FrameNumber())
print("Frame Time (when received) [s]", frame.FrameTime_seconds())
print("Frame Age (now - FrameTime) [s]", frame.FrameAge_seconds())


############################################################################################
# Get Object data from Frame
##############################################
# Get every object (return type: list of points)
print('Every Object:     ', end='')
print([point.Name() for point in frame.All()], sep=', ')

# Get every object that is visible in the current frame (return type: list of points)
print('Visible Objects:  ', end='')
print([point.Name() for point in frame.GetIfNotOccluded()], sep=', ')

# Get specific objects (Use the friendly names of the objects as specified in the allowList)
print('Specific Objects: ', end='')
print([point.Name() for point in frame.GetByNames(['Jackal', 'Pedestrian'])], sep=', ')

# Get a specific object
print()
point = frame.GetByName('Jackal')


############################################################################################
# Get Information about an Object
##############################################
# Name of object, as specified in the allowList
print('Name:', point.Name())

# Is the object occluded in this frame?
print('Is Occluded in this frame?:', point.IsOccluded())

# Translation [mm] (x, y, z, position vector, homogeneous position vector)
print('x [mm]:', point.x())
print('y [mm]:', point.y())
print('z [mm]:', point.z())
print('(x,y,z) [mm]:\n', point.P())
print('(x,y,z,1) [mm]:\n', point.Ph())

# Rotation (matrix, quaternions)
print('Rotation Matrix:\n', point.R())
print('Rotation quaternion (x,y,z,w):', point.quat_xyzw())
print('Rotation quaternion (w,x,y,z):', point.quat_wxyz())

# Transformation matrix [position in mm]
print('Transformation Matrix:\n', point.T())
print('Inverse of Transformation Matrix:\n', point.Inv().T())


ot.Disconnect()



