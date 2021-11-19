import socket
import common
import pickle
import os
import sys
import pandas as pd

BUFFER_SIZE = 1000
SERVER_PORTS = [1235, 1236, 1237, 1238, 1239]


def connect_to_server(port):
    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_socket.connect((socket.gethostname(), port))


def get_file_table():
    if not os.path.exists('tabela.csv'):
        df = pd.DataFrame(columns=['file_name', 'server_1', 'server_2',
                                   'server_3', 'server_4', 'server_5'])
        return df
    return pd.read_csv('tabela.csv')


def handle_deposito(data, s, df):
    # Se a conexão atual é no servidor principal,
    # manda o arquivo para os outros servidores
    if s.getsockname()[1] == common.MAIN_PORT:
        for index in range(int(data['tolerancia'])):
            new_socket = connect_to_server(SERVER_PORTS[index])
            new_socket.send(pickle.dumps(data))
            print(f'cópia {index} salva')
            file_in_table = df[df['file_name'] == data['file_name']]
            if not file_in_table.empty:
                row_index = file_in_table.index.values.astype(int)[0]
                empty_column = file_in_table.columns[file_in_table.isna(
                ).any()].tolist()[0]
                df.loc[row_index, empty_column] = int(SERVER_PORTS[index])
                print(empty_column)
                print(df)
            else:
                new_row = [data['file_name'], SERVER_PORTS[index],
                           None, None, None, None]
                df.loc[len(df)] = new_row
            df.to_csv('tabela.csv', index=False)
            # TODO: Salvar na tabela em qual porta o arquivo foi salva

    # Caso não seja o servidor principal salva o arquivo
    # numa pasta com nome port_{porta_do_servidor}
    else:
        file_name = os.path.join(
            "server", f'port_{s.getsockname()[1]}', data['file_name'])
        common.save_file(file_name, data['file'])


def handle_recuperacao(data, s, df):
    if s.getsockname()[1] == common.MAIN_PORT:
        pass
    else:
        print("uepa")


def handle_edicao(data):
    print("edicao")


def create_socket(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostname(), port))
    return s


def main():
    df = get_file_table()
    print(df)
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
            handle_deposito(data_rcvd, s, df)
            clientSocket.send(bytes(str('Arquivo salvo !'), 'utf-8'))
        if data_rcvd['operacao'] == "recuperacao":
            handle_recuperacao(data_rcvd)
        if data_rcvd['operacao'] == "edicao":
            handle_edicao(data_rcvd)

        clientSocket.close()


if __name__ == '__main__':
    main()
