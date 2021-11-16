import socket
import common
import pickle


operation = "deposito"
tolerance = 10
file = ""
file_name = "foto"

data = {'operacao': operation, 'tolerancia': tolerance, 'file_name': file_name}
data = pickle.dumps(data)
print(pickle.loads(data))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), common.server_port))

s.send(data)
msg = s.recv(1024)  # increase for large files
print(msg.decode("utf-8"))
