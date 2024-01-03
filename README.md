# linux-isolate-process
Isolates any given process using the ``unshare()`` system call. Suited for ROS, though can work for any process.
Since the system call is linux specific, this would not work on Windows.
This can be really useful for running a large number of tests in parallel wihtout having them interacting with each other.

This is similar to ROS domain IDs, though domain IDs are limited by the number of ports you have, and this approach is more scalable.

Originally added in [drake-ros](https://github.com/RobotLocomotion/drake-ros)

# Installation and usage

### From [PYPI](https://pypi.org/project/linux-isolate-process/)
```
pip install linux-isolate-process
```

### From source
```
git clone https://github.com/adityapande-1995/linux-isolate-process
cd linux-isolate-process
pip install .
```

### 1. This command can now be used as a commandline tool: 
```
linux_isolate_process <your command>
```

For example, to run an isolated talker (Note : any ros nodes inside the ``bash -c "(<command>)"`` will be able to talk to each other) : 
```
linux_isolate_process /bin/bash -c "ros2 run demo_nodes_cpp talker"
```
If you open another terminal and run a listener normally, using
```
ros2 run demo_nodes_cpp listener
```
it will not receive any of the messages published by the talker.

### 2. This can also be used as a module, to isolate the current process:
```
Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import linux_isolate_process as i
>>> i.create_linux_namespaces()
True
```

