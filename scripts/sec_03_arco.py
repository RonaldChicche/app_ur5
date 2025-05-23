from robolink import *       
from robodk import *         
from math import radians, cos, sin, pi, sqrt


# PARÁMETROS ---------------------------------------------------
center_pos = [600, 0, 600]
radius = 400
z = center_pos[2]
angle_start = radians(0) - pi/3
angle_via   = angle_start + radians(60)
angle_end   = angle_start + radians(120)
speed = 100
blend = 10  # mm

RDK = Robolink()
robot = RDK.Item('', ITEM_TYPE_ROBOT)
tool = RDK.Item("Generic Paint Sprayer", ITEM_TYPE_TOOL)
frame = RDK.Item("Frame 2", ITEM_TYPE_FRAME)
home_target = RDK.Item("Home", ITEM_TYPE_TARGET)

robot.setPoseFrame(frame)
robot.setTool(tool)
robot.setRounding(blend)

def normalize(v):
    norm = sqrt(sum([vi**2 for vi in v]))
    return [vi/norm for vi in v]

def pose_lookat(pos, target):
    z_axis = normalize([target[i] - pos[i] for i in range(3)])
    y_guess = [0, 0, -1]
    x_axis = normalize(cross(y_guess, z_axis))
    y_axis = normalize(cross(z_axis, x_axis))
    return Mat([
        [x_axis[0], y_axis[0], z_axis[0], pos[0]],
        [x_axis[1], y_axis[1], z_axis[1], pos[1]],
        [x_axis[2], y_axis[2], z_axis[2], pos[2]],
        [0,         0,         0,         1]
    ])

def point_on_arc(angle):
    x = center_pos[0] + radius * cos(angle)
    y = center_pos[1] + radius * sin(angle)
    return [x, y, z]

start_pos = point_on_arc(angle_start)
via_pos   = point_on_arc(angle_via)
end_pos   = point_on_arc(angle_end)

pose_start = pose_lookat(start_pos, center_pos)
pose_via   = pose_lookat(via_pos, center_pos)
pose_end   = pose_lookat(end_pos, center_pos)

t_start = RDK.AddTarget("03_Arc_Start", frame)
t_via   = RDK.AddTarget("03_Arc_Via", frame)
t_end   = RDK.AddTarget("03_Arc_End", frame)

t_start.setPose(pose_start)
t_via.setPose(pose_via)
t_end.setPose(pose_end)

# Programa -----------------------------------------------------
prog_set = RDK.AddProgram("Sec_03_Arco_Set", robot)
prog_set.setPoseFrame(frame)
prog_set.setTool(tool)
prog_set.setZoneData(blend)
prog_set.setSpeed(speed)
prog_set.MoveJ(t_start)

program = RDK.AddProgram("Sec_03_Arco_Go", robot)
program.setPoseFrame(frame)
program.setTool(tool)
program.setZoneData(blend)
program.setSpeed(speed)
program.MoveL(t_start)
program.MoveC(t_via, t_end)
program.MoveL(t_start)
program.MoveJ(home_target)

