# OptiTrack NatNet SDK - Template Projects (Not Official)
This repository contains instruction and template projects to use the OptiTrack NatNet SDK to stream 'Rigid Body' positions and orientations from the software OptiTrack Motive to user written software in realtime

Only the Python interface is provided. Only captures 'Rigid Body' objects, not skeletons

Note for ROS users: As an alternative to using the NatNet SDK, perhaps try the [vrpn_client_ros](http://wiki.ros.org/vrpn_client_ros)

Related Software
- [OptiTrack Motive](https://www.optitrack.com/support/downloads/motive.html)
	- Any version should work
	- The instructions were written based off Motive `2.0.2`
- [OptiTrack NatNet SDK](https://www.optitrack.com/support/downloads/developer-tools.html)
	- This project was written for version `4.0.0`. Past or future versions may not function the same


## Software Architecture
The directory `NatNetPython` holds a very slightly modified version of the OptiTrack NatNet SDK version `4.0.0` as well as my custom interface `OTInterface`

Each example project depends on this directory, but is otherwise stand-alone

### OTInterface
Provides an interface class [that wraps the SDK](https://en.wikipedia.org/wiki/Wrapper_function)

Features:
- Instead of setting your own `NatNetClient.new_frame_listener` callback, my interface retrieves and cache frames in a background thread, while providing 3 modes of retrieval
	- `GetFrame`
		- Instantly returns the latest cached frame. Will return the same frame again if called before a new frame arrives
		- Use when the call must not block (note: blocking means to pause the program)
		- e.g. need to receive frames while also sending commands to a robot at a higher frequency
	- `GetFrame_GetUnread`
		- If the cached frame has not yet been read, returns this frame instantly. Otherwise, blocks until a new frame arrives
		- Use when blocking is acceptable, but duplicate frames are not
		- e.g. a simple program to receive and write every frame to excel
	- `GetFrame_WaitForNew`
		- Blocks until a new frame arrives regardless of caching
		- Use to ensure minimal delay between receiving a frame to using its values
		- e.g. Synchronise frame data with reading other sensors
- Data is encoded in objects that can be managed easier while seamlessly handling calls to retrieve data from occluded objects

### Example Projects
1. Demonstrates the use of all functions provided by the interface
2. Loop and operate on the captured data
3. Loop and write the captured data into Excel


## Prerequisite Setup
### OptiTrack Control Computer
(The computer that is connected to the OptiTrack cameras)
1. OptiTrack Motive is installed on this computer
2. The OptiTrack system is set up, calibrated, and running
3. In Motive, data broadcasting is enabled
	1. Navigate to `Motive` > `view` > `Data Streaming`
	2. Activate `Broadcast Frame Data`
4. In Motive, Configure the Streaming ID of every object you wish to capture
	1. The streamed data identifies each object by its `Streaming ID`
	2. Navigate to `Motive` > `Rigid Body properties`
	3. Select each Rigid Body and assign its `Streaming ID`

### Client computer
(The computer you wish to work on | You may work directly on the OptiTrack Control Computer. The steps are the same.)
1. This computer is connected to the same network as the OptiTrack Control Computer
2. Download this git repository onto the computer
3. Setup python
	1. For beginners (like me), just install [PyCharm Community](https://www.jetbrains.com/pycharm/) or [Anaconda](https://www.anaconda.com/products/distribution)


## This Documentation
This documentation is written in markdown. Please view it on GitHub or with a markdown viewer.


## License
This work is distributed under the [Apache 2.0 License](./LICENSE.txt)

### Readme-NatNet.txt from the OptiTrack NatNet SDK
NaturalPoint, Inc.

The NatNet SDK is a simple Client/Server networking SDK for sending and receiving
data from Motive across networks.  NatNet uses the UDP protocol in conjunction
with either multicasting or point-to-point unicasting for transmitting data.

Please refer to the NatNet API USer's Guide for more information.
https://wiki.optitrack.com/index.php?title=NatNet_SDK

A list of changes made in each version can be found at the following website:
https://www.optitrack.com/support/downloads/developer-tools.html
