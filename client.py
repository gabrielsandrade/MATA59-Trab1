import socket
import common
import pickle
import os

BUFFER_SIZE = 1024

file_name = "especificacao_do_trabalho.pdf"
data = {'operacao': 'deposito', 'tolerancia': 3, 'file_name': file_name}
if data['operacao'] == 'deposito':
    file = common.get_file(file_name)
    data['file'] = file
data = pickle.dumps(data)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), common.MAIN_PORT))

s.send(data)

full_msg = b''
while True:
    msg = s.recv(BUFFER_SIZE)
    full_msg += msg
    if len(msg) < BUFFER_SIZE:
        print('Mensagem recebida')
        break
data_rcvd = (pickle.loads(full_msg))
if 'message' in data_rcvd:
    print(data_rcvd['message'])

if 'file' in data_rcvd:
    file_name = os.path.join('client', file_name)
    common.save_file('client', file_name, data_rcvd['file'])
    print('arquivo salvo na pasta "client"')

elif 'error' in data_rcvd:
    print('falha na requisição')
