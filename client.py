import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1235))

operation = "deposito"
tolerance = 5
file = ""
file_name = "foto"

s.send(f"{operation}\n{tolerance}\n{file_name}".encode())
print(
    f"Mensagem enviada : \n-----------\n{operation}\n{tolerance}\n{file_name}\n-----------\n")
msg = s.recv(1024)  # increase for large files
print(msg.decode("utf-8"))
