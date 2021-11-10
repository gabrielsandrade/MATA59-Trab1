import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1234))
s.send("salvar\nfoto".encode())
msg = s.recv(1024)  # increase for large files
print(msg.decode("utf-8"))
