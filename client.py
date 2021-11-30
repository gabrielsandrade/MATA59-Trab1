import socket
import common
import pickle
import os
import sys

BUFFER_SIZE = 1024

args = sys.argv[1:]
try:
    operacao = args[0]
    file_name = args[1]
    if (operacao == 'recuperacao'):
        tolerancia = 0
    else:
        tolerancia = int(args[2])
except:
    print("Para a executar a aplicação, digite python3 client.py 'operacao_que_deseja_realizar', 'nome_do_arquivo', 'tolerancia'")
    exit()

data = {'operacao': operacao,
        'tolerancia': tolerancia,
        'file_name': file_name}

if data['operacao'] == 'deposito':
    file = common.get_file(file_name)
    data['file'] = file

data = pickle.dumps(data)

print(operacao, file_name, tolerancia)

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
if 'error' in data_rcvd:
    print(data_rcvd['error'])
    exit()
if 'message' in data_rcvd:
    print(data_rcvd['message'])

if 'file' in data_rcvd:
    file_name = os.path.join('client', file_name)
    common.save_file('client', file_name, data_rcvd['file'])
    print('arquivo salvo na pasta "client"')
