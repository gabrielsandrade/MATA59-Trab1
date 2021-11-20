import socket
import common
import pickle
import os
import sys
import pandas as pd

BUFFER_SIZE = 1000
SERVER_PORTS = [1235, 1236, 1237, 1238, 1239]


def delete_file(port, file_name):
    pass


def check_file_in_table(df, file_name):
    return df[df['file_name'] == file_name]


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


def get_file_table():
    if not os.path.exists('tabela.csv'):
        df = pd.DataFrame(columns=['file_name', 'server_1', 'server_2',
                                   'server_3', 'server_4', 'server_5'])
        return df
    return pd.read_csv('tabela.csv')


def handle_deposito(data, s):
    df = get_file_table()
    # Se a conexão atual é no servidor principal,
    # manda o arquivo para os outros servidores
    if s.getsockname()[1] == common.MAIN_PORT:
        for index in range(int(data['tolerancia'])):
            new_socket = connect_to_server(SERVER_PORTS[index])
            new_socket.send(pickle.dumps(data))
            print(f'cópia {index} salva')
            file_in_table = check_file_in_table(df, data['file_name'])

            if not file_in_table.empty:
                row_index = file_in_table.index.values.astype(int)[0]
                empty_column = file_in_table.columns[file_in_table.isna(
                ).any()].tolist()[0]
                df.loc[row_index, empty_column] = int(SERVER_PORTS[index])

            else:
                new_row = [data['file_name'], SERVER_PORTS[index],
                           None, None, None, None]
                df.loc[len(df)] = new_row
            df.to_csv('tabela.csv', index=False)

    # Caso não seja o servidor principal salva o arquivo
    # numa pasta com nome port_{porta_do_servidor}
    else:
        folder = os.path.join("server", f'port_{s.getsockname()[1]}')
        file_name = os.path.join(folder, data['file_name'])
        common.save_file(folder, file_name, data['file'])


def handle_recuperacao(data, s, clientSocket):
    df = get_file_table()
    file_in_table = check_file_in_table(df, data['file_name'])
    if file_in_table.empty:
        clientSocket.send(bytes('Arquivo não encontrado no servidor', "utf-8"))
        return
    if s.getsockname()[1] == common.MAIN_PORT:
        # remove as colunas nulas
        file_in_table = file_in_table.dropna(1)
        # remove a coluna do nome do arquivo
        file_in_table = file_in_table.drop(axis=1, columns=['file_name'])
        # removendo as colunas de cima sobra só as colunas que dizem onde o arquivo tá salvo
        servers_to_search_file = file_in_table.values[0]
        for server in servers_to_search_file:
            try:
                file = request_file(s, server, data)
                if 'file' in file:
                    clientSocket.send(pickle.dumps(file))
                    return
            except:
                pass
        error = pickle.dumps({'error': 'arquivo não encontrado'})
        clientSocket.send(error)
    else:
        try:
            file_name = os.path.join(
                'server', f'port_{s.getsockname()[1]}', data['file_name'])
            file = common.get_file(file_name)
            clientSocket.send(pickle.dumps({'file': file}))
        except:
            print('arquivo não encontrado')
            clientSocket.send(pickle.dumps(
                {'error': 'arquivo não encontrado'}))


def handle_edicao(data):
    print("edicao")


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
            common.validate_params(data_rcvd)
            print(f"operacao : {data_rcvd['operacao']}")
            print(f"file_name : {data_rcvd['file_name']}")
        except ValueError as error:
            print(error)
            clientSocket.send(bytes(str(error), "utf-8"))
            clientSocket.close()
            continue

        if data_rcvd['operacao'] == "deposito":
            handle_deposito(data_rcvd, s)
            clientSocket.send(pickle.dumps({'message': 'Arquivo salvo !'}))
        if data_rcvd['operacao'] == "recuperacao":
            handle_recuperacao(data_rcvd, s, clientSocket)
        if data_rcvd['operacao'] == "edicao":
            handle_edicao(data_rcvd)

        clientSocket.close()


if __name__ == '__main__':
    main()
