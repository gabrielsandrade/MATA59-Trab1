import socket
import common
import pickle
import os
import sys
import pandas as pd
import numpy as np

BUFFER_SIZE = 1000
SERVER_PORTS = [1235, 1236, 1237, 1238, 1239]


def delete_file(port, file_name):
    print('deletar')
    file = os.path.join('server', f'port_{port}', file_name)
    os.remove(file)


def check_file_in_table(df, file_name):
    return df[df['file_name'] == file_name]


def file_adresses(df):
    df.dropna(1)
    servers_to_search_file = df.drop(
        axis=1, columns=['file_name'])
    servers_to_search_file = servers_to_search_file.values[0]
    return servers_to_search_file


def request_file(s, port, data):
    new_socket = connect_to_server(port)
    new_socket.send(pickle.dumps(data))
    full_msg = b''
    while True:
        msg = new_socket.recv(BUFFER_SIZE)
        full_msg += msg
        if len(msg) < BUFFER_SIZE:
            break

    return pickle.loads(full_msg)


def connect_to_server(port):
    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_socket.connect((socket.gethostname(), port))
    return new_socket


def get_table():
    if not os.path.exists('tabela.csv'):
        df = pd.DataFrame(columns=['file_name', 'server_1', 'server_2',
                                   'server_3', 'server_4', 'server_5'])
        return df
    return pd.read_csv('tabela.csv')


def handle_deposito(data, s):
    # Se a conexão atual é no servidor principal,
    # manda o arquivo para os outros servidores
    if s.getsockname()[1] == common.MAIN_PORT:
        df = get_table()
        file_in_table = check_file_in_table(df, data['file_name'])
        file_in_table = file_in_table.dropna(1)
        file_in_table = file_in_table.drop(axis=1, columns=['file_name'])
        try:
            servers_to_search_file = file_in_table.values[0]
        except:
            servers_to_search_file = []

        servers_to_save_file = list(
            set(SERVER_PORTS) - set(servers_to_search_file))

        print(servers_to_save_file)
        for index in range(int(data['tolerancia'])):
            new_socket = connect_to_server(servers_to_save_file[index])
            new_socket.send(pickle.dumps(data))

            print(f'cópia {index + 1} salva')
            # preenche na tabela onde o arquivo foi salvo

            file_in_table = check_file_in_table(df, data['file_name'])
            if not file_in_table.empty:
                row_index = file_in_table.index.values.astype(int)[0]
                empty_column = file_in_table.columns[file_in_table.isna(
                ).any()].tolist()[0]
                df.loc[row_index, empty_column] = str(
                    servers_to_save_file[index])
                print(
                    f'coluna nova : linha : {row_index}, coluna : {empty_column}, -- {servers_to_save_file[index]}')

            else:
                print('aaaaaa')
                new_row = [data['file_name'], str(servers_to_save_file[index]),
                           np.nan, np.nan, np.nan, np.nan]
                df.loc[len(df)] = new_row
            df.to_csv('tabela.csv', index=False)

    # Caso não seja o servidor principal salva o arquivo
    # numa pasta com nome port_{porta_do_servidor}
    else:
        folder = os.path.join("server", f'port_{s.getsockname()[1]}')
        file_name = os.path.join(folder, data['file_name'])
        common.save_file(folder, file_name, data['file'])

    return {}


def handle_recuperacao(data, s):
    df = get_table()
    file_in_table = check_file_in_table(df, data['file_name'])
    if file_in_table.empty:
        return {'error': 'Arquivo não encontrado no servidor'}
    if s.getsockname()[1] == common.MAIN_PORT:
        # remove as colunas nulas
        file_in_table = file_in_table.dropna(1)
        # remove a coluna do nome do arquivo
        file_in_table = file_in_table.drop(axis=1, columns=['file_name'])
        # removendo as colunas de cima sobra só as colunas que dizem onde o arquivo tá salvo
        servers_to_search_file = file_in_table.values[0]
        for server in servers_to_search_file:
            try:
                file = request_file(s, int(server), data)
                if 'file' in file:
                    return file
            except:
                pass
        return {'error': 'arquivo não encontrado'}
    else:
        try:
            file_name = os.path.join(
                'server', f'port_{s.getsockname()[1]}', data['file_name'])
            file = common.get_file(file_name)
            return {'file': file}
        except:
            print('arquivo não encontrado')
            return {'error': 'arquivo não encontrado'}


def handle_edicao(data, s):
    if s.getsockname()[1] == common.MAIN_PORT:
        # se for o servidor principal :
        # - checar se o arquivo existe na tabela
        # - checar se a quantidade de vezes que o arquivo está duplicado no servidor é maior que ou menor que a solicitacao do usuario
        # - se for maior, devemos mandar mensagem pros servidores deletarem até as quantidades serem iguais
        # - se a quantidade for menor, pegar o arquivo em algum dos servidores e mandar para outros até as quantidades serem iguais

        df = get_table()
        file_in_table = check_file_in_table(df, data['file_name'])
        if file_in_table.empty:
            print('enviar erro')
            # enviar erro pro usuario
            return

        file_in_table = file_in_table.dropna(1)
        file_in_table = file_in_table.drop(axis=1, columns=['file_name'])
        servers_to_search_file = file_in_table.values[0]

        servers_to_save_file = list(
            set(SERVER_PORTS) - set(servers_to_search_file))

        if len(servers_to_search_file) == data['tolerancia']:
            print('cheguei aqui')
            return

        if len(servers_to_search_file) > data['tolerancia']:
            print('deletar de alguns servidores')
            delete_n_times = len(servers_to_search_file) - data['tolerancia']
            for n in range(delete_n_times):
                new_socket = connect_to_server(servers_to_search_file[n])
                data = {'operacao': 'deletar',
                        'file_name': data['file_name']}
                new_socket.send(pickle.dumps(data))
            return

        if len(servers_to_search_file) < data['tolerancia']:
            print('replicar para outros servidores')
            server_data = handle_recuperacao(
                {'operacao': 'recuperacao', 'file_name': data['file_name']}, s)
            if 'error' in server_data:
                return {'error': 'Arquivo não encontrado no servidor'}
            elif server_data['file']:
                print('fazer depósito -- ',
                      data['tolerancia'] - len(servers_to_search_file))
                data = handle_deposito(
                    {'operacao': 'deposito', 'file_name': data['file_name'],
                     'tolerancia': data['tolerancia'] - len(servers_to_search_file), 'file': server_data['file']}, s)
                return {'message': 'sucesso'}


def create_socket(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostname(), port))
    return s


def main():
    args = sys.argv[1:]
    if args and args[0] == "main":
        server_port = common.MAIN_PORT
        try:
            s = create_socket(server_port)
        except OSError as e:
            if e.errno == 98:
                print(f"Porta {server_port} já está em uso")
                exit()
    else:
        for port in SERVER_PORTS:
            #SERVER_PORTS = [1235, 1236, 1237, 1238, 1239]
            try:
                s = create_socket(port)
                break
            except OSError as e:
                if e.errno == 98:
                    print(f"Porta {port} já está em uso")
    if not s:
        exit()

    print(f"Servidor ativo na porta {s.getsockname()[1]}")
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
            # common.validate_params(data_rcvd)
            print(f"operacao : {data_rcvd['operacao']}")
            print(f"file_name : {data_rcvd['file_name']}")
        except ValueError as error:
            print(error)
            clientSocket.send(pickle.dumps({'error': str(error)}))
            clientSocket.close()
            continue

        if data_rcvd['operacao'] == "deposito":
            data = handle_deposito(data_rcvd, s)
            if 'error' in data:
                clientSocket.send(pickle.dumps(data))
            else:
                clientSocket.send(pickle.dumps({'message': 'Arquivo salvo !'}))
        if data_rcvd['operacao'] == "recuperacao":
            data = handle_recuperacao(data_rcvd, s)
            clientSocket.send(pickle.dumps(data))
        if data_rcvd['operacao'] == "edicao":
            handle_edicao(data_rcvd, s)
            clientSocket.send(pickle.dumps(
                {'message': 'implementar isso aqui'}))
        if data_rcvd['operacao'] == 'deletar':
            delete_file(s.getsockname()[1], data_rcvd['file_name'])

        clientSocket.close()


if __name__ == '__main__':
    main()
