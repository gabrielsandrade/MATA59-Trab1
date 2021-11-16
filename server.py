import socket
import common
import pickle
import os

BUFFER_SIZE = 1000


def handle_deposito(data):
    for index in range(int(data_rcvd['tolerancia'])):
        common.create_folder("server", str(index))
        file_name = os.path.join("server", str(index), data['file_name'])
        common.save_file(file_name, data['file'])
        print(f'cópia {index} salva')


def handle_recuperacao(data):
    print("uepa")


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), common.server_port))
s.listen(5)

while True:
    clientSocket, address = s.accept()
    print(f"Conexão estabelecida : {address}")

    full_msg = b''
    while True:
        msg = clientSocket.recv(BUFFER_SIZE)
        full_msg += msg
        if len(msg) < BUFFER_SIZE:
            print('Mensagem recebida')
            break
    try:
        data_rcvd = pickle.loads(full_msg)
        common.validate_params(data_rcvd)
        print(f"operacao : {data_rcvd['operacao']}")
        print(f"tolerancia : {data_rcvd['tolerancia']}")
        print(f"file_name : {data_rcvd['file_name']}")
    except ValueError as error:
        print(error)
        clientSocket.send(bytes(str(error), "utf-8"))
        clientSocket.close()
        continue

    if data_rcvd['operacao'] == "deposito":
        handle_deposito(data_rcvd)
    if data_rcvd['operacao'] == "recuperacao":
        handle_recuperacao(data_rcvd)
    clientSocket.close()
