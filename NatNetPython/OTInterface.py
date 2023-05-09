# NOTES
#   Streaming ID: value assigned in Motive > Rigid Body properties > Streaming ID
#   P: position vector
#   R_quat: rotation as a quaternion

# Units: mm and rad


from NatNetPython.NatNetClient import NatNetClient
import threading
import sys
import time
import copy
import numpy
from numpy import nan
import scipy


############################################################################################
# Data Structures
##############################################
class Point:
    def __init__(self,
                 Name:str,
                 R=numpy.array([nan,nan,nan,nan,nan,nan,nan,nan,nan]).reshape(3,3),
                 P=numpy.array([[nan,nan,nan]]).T):
        # The Name of the object in the allow list
        # Flag for if the object was not detected for this frame
        self._name = Name
        self._isOccluded = numpy.all(numpy.isnan(R)) and numpy.all(numpy.isnan(P))

        # Rotation matrix in OptiTrack Motive global frame
        # Position in OptiTrack Motive global frame
        self._R = R
        self._P = P

    def Name(self): return self._name
    def IsOccluded(self): return self._isOccluded

    def x(self): return self._P[0]
    def y(self): return self._P[1]
    def z(self): return self._P[2]

    def P(self): return self._P
    def Ph(self): return numpy.append(self._P, [[1]], axis=0)

    def R(self): return self._R
    def quat_xyzw(self): return scipy.spatial.transform.Rotation.from_matrix(self._R).as_quat()
    def quat_wxyz(self): return self.quat_xyzw().take([3,0,1,2])

    def T(self): return numpy.append( numpy.append(self._R, [[0, 0, 0]], axis=0), self.Ph(), axis=1)

    def Inv(self):
        R_transpose = self._R.T
        return Point(
            Name=self._name + '_inv',
            R=R_transpose,
            P=-R_transpose @ self._P
        )


class Points:
    def __init__(self, frameNumber=nan, frameTime_seconds=nan):
        self._frameNumber = frameNumber
        self._frameTime_seconds = frameTime_seconds
        self._all = {}

    def FrameNumber(self): return self._frameNumber
    def FrameTime_seconds(self): return self._frameTime_seconds
    def FrameAge_seconds(self): return time.time() - self._frameTime_seconds

    def All(self): return list(self._all.values())
    def All_dict(self): return self._all

    def AddPoint(self, point):
        self._all[point.Name()] = point

    def GetByName(self, name:str):
        if name in self._all:
            # Get from frame data
            return self._all[name]
        else:
            # Create new as occluded
            return Point(name)

    def GetByNames(self, names):
        out = []
        for name in names:
            out.append( self.GetByName(name) )
        return out

    def GetIfNotOccluded(self):
        out = []
        for point in self._all:
            if point.IsOccluded():
                out.append(point)
        return out


############################################################################################
# Interface
##############################################
class Interface:
    def __init__(self, clientAddress="127.0.0.1", serverAddress="127.0.0.1"):
        self.clientAddress = clientAddress
        self.serverAddress = serverAddress
        self.use_multicast = True

        # Dictionary with
        #   key = Streaming ID
        #   val = friendly name (used as the key in returned frames)
        self.allowList = {}

        self.client = NatNetClient()
        self.client.set_client_address(self.clientAddress)
        self.client.set_server_address(self.serverAddress)
        self.client.set_use_multicast(self.use_multicast)
        self.client.set_print_level(0) # Data that gets automatically printed. 0=minimal

        # Internal
        self._IsConnected = False
        self._IsFrameReady = threading.Event()
        self._HasLatestFrameBeenRead = threading.Event()
        self._LatestFrame = Points()
        self._lock = threading.Lock()

        # Attach callback
        #   Callbacks are run in a separate thread
        self.client.new_frame_listener = self._UpdateFrameInBackground

    def __del__(self):
        self.Disconnect()

    #********************************************************************************
    # Interface: Connect / Disconnect
    #****************************************
    def Connect(self):
        if self._IsConnected: return

        self._IsFrameReady.clear()
        self._HasLatestFrameBeenRead.clear()
        
        success = self.client.run()
        if not success:
            print("ERROR_OT: Could not start streaming client.")
            sys.exit(1)

        time.sleep(1)
        if self.client.connected() is False:
            print("ERROR_OT: Could not connect properly.  Check that Motive streaming is on.")
            sys.exit(2)
        
        self._IsConnected = True

        # Get first frame to initialise
        self.GetFrame()

        print("INFO_OT: Ready to capture data")

    def Disconnect(self):
        if not self._IsConnected: return
        self.client.shutdown()
        self._IsConnected = False
        print("INFO_OT: Client is now Disconnected")

    #********************************************************************************
    # Interface: Get data frames
    #****************************************
    # PURPOSE:
    #	Same as GetFrame() but blocks until the next frame arrives
    def GetFrame_WaitForNew(self):
        self._IsFrameReady.clear()
        return self.GetFrame()

    # PURPOSE:
    #	Same as GetFrame() but
    #		If the latest frame has not yet been read, return the cached frame
    #		Otherwise, block until the next unread frame arrives
    def GetFrame_GetUnread(self):
        if self._HasLatestFrameBeenRead.is_set(): self._IsFrameReady.clear()
        return self.GetFrame()

    # PURPOSE:
    #	Get next data frame
    # OUTPUT: Points object holding the captured data.
    def GetFrame(self):
        if not self._IsConnected:
            print("WARNING_OT: (GetFrame) Not Connected")
            return Points()

        # Block until thread signals ready
        self._IsFrameReady.wait()

        with self._lock:
            LatestFrame_copy = copy.deepcopy(self._LatestFrame)

        self._HasLatestFrameBeenRead.set()
        return LatestFrame_copy

    # ************************************************************
    # Frame update thread
    # ******************************
    # Callback function that gets connected to the NatNet client.
    # Is called once per mocap frame.
    def _UpdateFrameInBackground(self, data):
        # Create object holding frame data
        Frame = Points(data['frame_number'], time.time())
        
        for rigid_body in data["rigid_body_data"].rigid_body_list:
            if not rigid_body.tracking_valid:
                continue
            
            if rigid_body.id_num in self.allowList:
                name = self.allowList[rigid_body.id_num]

                # OptiTrack is in meters, but Vicon in mm, so convert to mm (either way is good, but meh)
                P = numpy.array([rigid_body.pos]).T * 1000

                # OptiTrack encodes rotation as a quaternion of form [x,y,z,w]
                # SciPy quaternions are of form [x,y,z,w]
                # => no need to change yay
                R = numpy.asarray(
                    scipy.spatial.transform.Rotation.from_quat(rigid_body.rot).as_matrix(),
                    order='C'
                )

                point = Point(name, R, P)
                Frame.AddPoint(point)

                # print(rigid_body.rot)
                # print(tuple(point.quat_xyzw()))
                # print(tuple(point.quat_wxyz()))
                # print('-------------')
        
        # Replace public reference to the previous frame with the new frame
        with self._lock:
            self._LatestFrame = Frame
        
        # Unblock GetFrame()
        self._HasLatestFrameBeenRead.clear()
        self._IsFrameReady.set()


if __name__ == "__main__":
    ot = Interface()
    ot.allowList[100] = 'Jackal'
    ot.allowList[101] = 'Pedestrian'
    
    ot.Connect()

    frame = ot.GetFrame()
    j = frame.GetByName('Jackal')
    p = frame.GetByName('Pedestrian')
    print(frame.FrameNumber())
    print(j.Name())
    print(j.T())
    print(p.Name())
    print(p.T())

    print('All points:')
    for point in frame.All():
        print(point.Name(), point.P().T)

    # Test running for a short while
    for idx in range(1,50):
        print( ot.GetFrame_GetUnread().FrameNumber() )

    ot.Disconnect()

