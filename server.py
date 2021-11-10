import socket
import common

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 1234))
s.listen(5)

while True:
    clientSocket, address = s.accept()
    print(f"Conexão estabelecida : {address}")

    parameters = clientSocket.recv(1024).decode()
    parameters = parameters.splitlines()

    # Check parameters
    if(len(parameters) < 2):
        clientSocket.send(bytes("Parametros inválidos", "utf-8"))
        clientSocket.close()

    print(parameters)
    if parameters[0] == "salvar":
        common.create_folder("server", parameters[1])
        print(f"Pasta criada : {parameters[1]}")
    
    if parameters[0] == "":
        print("uepa")
    clientSocket.close()
