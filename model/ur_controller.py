import socket
import struct
import time

class DashboardClient:
    def __init__(self, ip, port=29999):
        self.ip = ip
        self.port = port

    def send_command(self, command, timeout=3):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((self.ip, self.port))
            s.recv(1024)  # bienvenida
            s.sendall((command + "\n").encode())
            return s.recv(1024).decode().strip()

    def load_program(self, path):
        return self.send_command(f"load {path}")

    def play(self):
        return self.send_command("play")

    def pause(self):
        return self.send_command("pause")

    def stop(self):
        return self.send_command("stop")
    
    def unlock_protective_unlock(self):
        return self.send_command("unlock protective stop")

    def is_connected(self):
        try:
            self.robot_mode()  # prueba de conexión
            print("[✓] Conectado al Dashboard")
            return True
        except Exception as e:
            print("[X] Fallo al conectar:", e)
            return False

    def robot_mode(self):
        return self.send_command("robotmode")
    
    def program_state(self):
        return self.send_command("programState")
    
    def safety_status(self):
        return self.send_command("safetystatus")

    def is_robot_ready(self):
        mode = self.robot_mode().lower()
        return "running" in mode or "normal" in mode

    def power_on(self):
        return self.send_command("power on")

    def brake_release(self):
        return self.send_command("brake release")

    def unlock_protective_stop(self):
        return self.send_command("unlock protective stop")

    def auto_initialize(self):
        print("→ Iniciando secuencia de desbloqueo y encendido")
        time.sleep(3)
        self.power_on()
        self.unlock_protective_stop()
        time.sleep(1)
        self.brake_release()
        print("✓ Robot listo")


class URScriptInterface:
    def __init__(self, ip, script_port=30002, state_port=30003):
        self.ip = ip
        self.script_port = script_port
        self.state_port = state_port

    def send_script_file(self, file_path):
        with open(file_path, 'r') as f:
            script = f.read()
        return self.send_script(script)

    def send_script(self, script_text):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip, self.script_port))
            s.sendall(script_text.encode('utf-8'))
            return "Script sent successfully."

    def send_command(self, command):
        """
        Enviar un solo comando URScript.
        """
        if not command.endswith('\n'):
            command += '\n'
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip, self.script_port))
            s.sendall(command.encode('utf-8'))
            return True

    def receive_tcp_pose(self):
        """
        Devuelve la pose TCP actual del robot como una tupla de 6 valores (x, y, z, Rx, Ry, Rz).
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip, self.state_port))
            data = s.recv(1116)  # tamaño típico del paquete de estado en robots UR e-Series
            tcp_pose_bytes = data[444:444 + 48]  # 6 valores double
            tcp_pose = struct.unpack('dddddd', tcp_pose_bytes)
            return tcp_pose

    def get_tcp_pose_str(self):
        """
        Imprime la pose TCP actual del robot.
        """
        pose = self.receive_tcp_pose()
        print("TCP Pose:", pose)
        return pose


class URRobotController:
    def __init__(self, ip):
        self.dashboard = DashboardClient(ip)
        self.script_sender = URScriptInterface(ip)

    def load_and_run(self, program_path):
        self.dashboard.load_program(program_path)
        return self.dashboard.play()
    
    def send_comand(self, command:str):
        confirmation = self.script_sender.send_command(command=command)
        if confirmation:
            print("Enviado exitosamente:", command)
        else:
            print(" X Error en el envio")

    def send_script_file(self, script_text):
        return self.script_sender.send_script_file(script_text)

    def stop(self):
        return self.dashboard.stop()

    def pause(self):
        return self.dashboard.pause()
    
    def play(self):
        return self.dashboard.play()
    
    def unlock_protective_unlock(self):
        return self.dashboard.unlock_protective_unlock()
    
    def auto_initialize(self):
        self.dashboard.auto_initialize()
