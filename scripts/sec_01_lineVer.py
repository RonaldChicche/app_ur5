from robolink import *
from robodk import *
from math import sqrt


# PARÁMETROS ---------------------------------------------------
p_high = [1100, -250, 900]     # Punto elevado (inicio del zoom)
p_low = [800, -200, 600]       # Punto más bajo
center = [700, -150, 600]      # Punto de enfoque de la herramienta
speed = 100 
blend = 10

# Inicializar 
RDK = Robolink()
robot = RDK.Item('', ITEM_TYPE_ROBOT)
tool = RDK.Item("Generic Paint Sprayer", ITEM_TYPE_TOOL)
frame = RDK.Item("Frame 2", ITEM_TYPE_FRAME)
home_target = RDK.Item("Home", ITEM_TYPE_TARGET)

robot.setPoseFrame(frame)
robot.setTool(tool)
robot.setRounding(blend)

def look_at_orientation(pos, target):
    z_axis = normalize3([target[i] - pos[i] for i in range(3)])
    y_guess = [0, 0, -1]
    x_axis = normalize3(cross(y_guess, z_axis))
    y_axis = normalize3(cross(z_axis, x_axis))
    return Mat([
        [x_axis[0], y_axis[0], z_axis[0], pos[0]],
        [x_axis[1], y_axis[1], z_axis[1], pos[1]],
        [x_axis[2], y_axis[2], z_axis[2], pos[2]],
        [0,         0,         0,         1]
    ])

# Movimiento alto → bajo mirando al centro
pose_high = look_at_orientation(p_high, center)
pose_low  = look_at_orientation(p_low, center)

t_high = RDK.AddTarget("01_ZoomIn_Start", frame)
t_low  = RDK.AddTarget("01_ZoomIn_End", frame)
t_high.setPose(pose_high)
t_low.setPose(pose_low)

# Programa -----------------------------------------------------
prog_set = RDK.AddProgram("Sec_01_LineaVer_Set", robot)
prog_set.setPoseFrame(frame)
prog_set.setTool(tool) 
prog_set.setZoneData(blend)
prog_set.setSpeed(speed)
prog_set.MoveL(t_high)

program = RDK.AddProgram("Sec_01_LineaVer_Go", robot)
program.setPoseFrame(frame)
program.setTool(tool) 
program.setZoneData(blend)
program.setSpeed(speed)
program.MoveL(t_high)
program.MoveL(t_low)
program.MoveL(t_high)
program.MoveJ(home_target)

