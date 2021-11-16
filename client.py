import socket
import common
import pickle


operation = "deposito"
tolerance = 2
file = ""
file_name = "foto.png"
data = {'operacao': operation, 'tolerancia': tolerance, 'file_name': file_name}
file = common.get_file(file_name)
data['file'] = file
data = pickle.dumps(data)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), common.server_port))

s.send(data)
msg = s.recv(1024)  # increase for large files
print(msg.decode("utf-8"))
