from robolink import *
from robodk import *
from math import sqrt, atan2, pi, cos, sin


# PARÁMETROS ---------------------------------------------------
p_high = [900, -250, 900]     # Punto elevado (inicio del zoom)
p_low = [700, -150, 600]      # Punto más bajo, e inicio del arco
center = [550, 0, 600]   # Centro del cuarto de circunferencia
speed = 100 
blend = 10

# Inicializar RoboDK
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


# Movimiento de acercamiento
pose_high = look_at_orientation(p_high, center)
pose_low = look_at_orientation(p_low, center)

t_high = RDK.AddTarget("04_ZoomIn_Start", frame)
t_low = RDK.AddTarget("04_ZoomIn_End", frame)
t_high.setPose(pose_high)
t_low.setPose(pose_low)

# Trayectoria con MoveC ---------------------------------
# Paso 1: calcular ángulo inicial (desde p_low hacia centro)
dx = p_low[0] - center[0]
dy = p_low[1] - center[1]
start_angle = atan2(dy, dx)
end_angle = start_angle + pi / 2  # 90°

# Paso 2: calcular punto intermedio y final sobre el arco
radius = sqrt((dx)**2 + (dy)**2)
angle_via = start_angle + (end_angle - start_angle) * 0.5
angle_end = end_angle

# Vía (45°)
via = [
    center[0] + radius * cos(angle_via),
    center[1] + radius * sin(angle_via),
    center[2]
]

# Final (90°)
end = [
    center[0] + radius * cos(angle_end),
    center[1] + radius * sin(angle_end),
    center[2]
]

pose_via = look_at_orientation(via, center)
pose_end = look_at_orientation(end, center)

t_via = RDK.AddTarget("04_Arc_Via", frame)
t_end = RDK.AddTarget("04_Arc_End", frame)

t_via.setPose(pose_via)
t_end.setPose(pose_end)

# Programa --------------------------------------------
program = RDK.AddProgram("Sec_04_Complex_Set", robot)
program.setPoseFrame(frame)
program.setTool(tool) 
program.setZoneData(blend)
program.setSpeed(speed)
program.MoveL(t_high)

program = RDK.AddProgram("Sec_04_Complex_Go", robot)
program.setPoseFrame(frame)
program.setTool(tool) 
program.setZoneData(blend)
program.setSpeed(speed)
program.MoveL(t_high)
program.MoveL(t_low)
program.MoveC(t_via, t_end)
program.MoveL(t_low)
program.MoveJ(home_target)
