import socket
import common
import pickle

BUFFER_SIZE = 1024

file_name = "especificacao_do_trabalho.pdf"
data = {'operacao': 'deposito',
        'tolerancia': 2,
        'file_name': file_name}
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
print(msg.decode("utf-8"))
