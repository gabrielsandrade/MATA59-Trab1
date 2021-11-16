# File with common functions
import os

suportted_methods = ["deposito", "recuperacao"]
server_port = 1233


def create_folder(type, folder_name):
    folder = os.path.join(type, folder_name)
    if not os.path.exists(folder):
        os.makedirs(folder)


# TODO: Criar método para salvar arquivo enviado pelo cliente
def save_file(file_name):
    return


# TODO: Criar método para pegar arquivo buscado pelo cliente
def get_file(file_name):
    return


def validate_params(params):
    if params['operacao'] not in suportted_methods:
        raise ValueError("Método solicitado inválido")
