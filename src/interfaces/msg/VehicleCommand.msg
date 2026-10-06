std_msgs/Header header
float32 throttle    # 0.0 .. 1.0
float32 brake       # 0.0 .. 1.0
float32 steer       # -1.0 .. 1.0, positive = left
bool reverse
bool hand_brake

# Normalized actuator command, sent by control, consumed by the sim (or the real car driver).
# ROS conventions: positive steer = left (counter-clockwise), as in REP-103.