# File with common functions
import os

suportted_methods = ["deposito", "recuperacao"]
server_port = 1235


def create_folder(type, folder_name):
    folder = os.path.join(type, folder_name)
    if not os.path.exists(folder):
        os.makedirs(folder)


def save_file(file_name, file):
    with open(file_name, 'wb') as f:
        f.write(file)
    return


def get_file(file_name):
    with open(file_name, 'rb') as file:
        return file.read()


def validate_params(params):
    if params['operacao'] not in suportted_methods:
        raise ValueError("Método solicitado inválido")
