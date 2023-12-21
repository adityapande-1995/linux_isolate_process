# isolate-ros
Isolates any given process using the unshare system call. Suited for ROS, though can work for any process.
Since the system call is linux specific, this would not work on Windows.
This can be really useful for running a large number of tests in parallel wihtout having them interacting with each other.

This is similar to ROS domain IDs, though domain IDs are limited by the number of ports you have, and this approach is more scalable.

Originally added in [drake-ros](https://github.com/RobotLocomotion/drake-ros)

# Installation and usage
```
git clone https://github.com/adityapande-1995/isolate-ros.git
pip install isolate-ros
```

This command can now be used as : 
```
isolate_ros <your command>
```

For example, to run an isolated talker (Note : any ros inside the ``bash -c "(<command>)" will be able to talk to each other) : 
```
isolate_ros /bin/bash -c "ros2 run demo_nodes_cpp talker"
```
If you open another terminal and run a listener normally, using
```
ros2 run demo_nodes_cpp listener
```
it will not receive any of the messages published by the talker.
