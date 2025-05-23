from robolink import *
from robodk import *
from math import radians, pi, sqrt


# PARÁMETROS -----------------------------------------------------------------------
center = [800, 0, 800]   # centro de la línea (X, Y, Z)
length = 300              # longitud total (en eje Y)
lookat_offset = -200      # distancia en X desde la línea al punto a observar (→ eje rojo)
speed = 100               # mm/s
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
    y_guess = [0, 0, -1]  # para que Y (verde) mire hacia abajo
    x_axis = normalize3(cross(y_guess, z_axis))
    y_axis = normalize3(cross(z_axis, x_axis))

    return Mat([
        [x_axis[0], y_axis[0], z_axis[0], pos[0]],
        [x_axis[1], y_axis[1], z_axis[1], pos[1]],
        [x_axis[2], y_axis[2], z_axis[2], pos[2]],
        [0,         0,         0,         1]
    ])

# Calcular extremos de la línea en eje Y
half = length / 2
p_start = [center[0], center[1] - half, center[2]]
p_end   = [center[0], center[1] + half, center[2]]

# Punto a observar (desplazado en eje X)
lookat_point = [center[0] + lookat_offset, center[1], center[2]]

pose_start = look_at_orientation(p_start, lookat_point)
pose_end   = look_at_orientation(p_end, lookat_point)

t_start = RDK.AddTarget("02_LineY_Start", frame)
t_end = RDK.AddTarget("02_LineY_End", frame)

t_start.setPose(pose_start)
t_end.setPose(pose_end)

# Programa ---------------------------------------------------
prog_set = RDK.AddProgram("Sec_02_LineaHor_Set", robot)
prog_set.setPoseFrame(frame)
prog_set.setTool(tool)
prog_set.setZoneData(blend)
prog_set.setSpeed(speed)
prog_set.MoveL(t_start)

program = RDK.AddProgram("Sec_02_LineaHor_Go", robot)
program.setPoseFrame(frame)
program.setTool(tool)
program.setZoneData(blend)
program.setSpeed(speed)
program.MoveL(t_start)
program.MoveL(t_end)
program.MoveL(t_start)
program.MoveJ(home_target)

