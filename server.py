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

    try:
        common.validate_params(parameters)
    except ValueError as error:
        print(error)
        clientSocket.send(bytes(str(error), "utf-8"))
        clientSocket.close()
        continue
    # Check parameters
    if(len(parameters) < 2):
        clientSocket.send(bytes("Parametros inválidos", "utf-8"))
        clientSocket.close()

    print(parameters)
    if parameters[0] == "deposito":
        for index in range(int(parameters[1])):
            common.create_folder("server", str(index))
        print(f"Pastas criadas : {(parameters[1])}")

    if parameters[0] == "recuperacao":
        print("uepa")
    clientSocket.close()
