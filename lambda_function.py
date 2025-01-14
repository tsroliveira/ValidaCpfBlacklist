import json
import boto3
from datetime import datetime

s3 = boto3.client('s3')
BUCKET_NAME = 'cpfblacklist'
BLACKLIST_FILE = 'blacklist.csv'

# Função para validar o CPF
def valida_cpf(str_cpf):
    if len(str_cpf) != 11 or not str_cpf.isdigit():
        return False
    
    if str_cpf == str_cpf[0] * 11:
        return False

    soma = sum([int(str_cpf[i]) * (10 - i) for i in range(9)])
    resto = (soma * 10) % 11
    if resto == 10 or resto == 11:
        resto = 0
    if resto != int(str_cpf[9]):
        return False

    soma = sum([int(str_cpf[i]) * (11 - i) for i in range(10)])
    resto = (soma * 10) % 11
    if resto == 10 or resto == 11:
        resto = 0
    if resto != int(str_cpf[10]):
        return False

    return True


# Função para verificar se o CPF está na blacklist
def verifica_blacklist(cpf):
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=BLACKLIST_FILE)
        content = response['Body'].read().decode('utf-8')
        for line in content.splitlines():
            if line.startswith(cpf):
                return True
    except s3.exceptions.NoSuchKey:
        pass
    return False


# Função para adicionar ou remover CPF da blacklist
def atualizar_blacklist(cpf, motivo, action):
    # Verificar se o CPF é válido antes de qualquer ação
    if not valida_cpf(cpf):
        return {"status": "CPF_INVALIDO"}

    try:
        # Tentar obter o conteúdo existente do arquivo
        response = s3.get_object(Bucket=BUCKET_NAME, Key=BLACKLIST_FILE)
        content = response['Body'].read().decode('utf-8')
        lines = content.splitlines()
    except s3.exceptions.NoSuchKey:
        # Caso o arquivo não exista, inicializa uma lista vazia
        content = ""
        lines = []

    # Lidar com a ação de adicionar CPF
    if action == "ADD":
        # Verificar se o CPF já está na blacklist
        for line in lines:
            if line.startswith(cpf):
                return {"status": "CPF_EXISTENTE_NA_BLACKLIST"}

        # Adiciona o novo CPF, motivo e data
        data = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        linha = f"{cpf},{motivo},{data}\n"
        content += linha  # Adiciona o novo registro ao conteúdo existente
        s3.put_object(Bucket=BUCKET_NAME, Key=BLACKLIST_FILE, Body=content.encode('utf-8'))

        return {"status": "CPF_ADICIONADO_BLACKLIST"}

    # Lidar com a ação de remover CPF
    elif action == "REMOVE":
        # Verificar se o CPF está na blacklist
        cpf_encontrado = False
        updated_lines = []
        
        for line in lines:
            if line.startswith(cpf):
                cpf_encontrado = True
            else:
                updated_lines.append(line)
        
        # Se o CPF não for encontrado, retorna a mensagem apropriada
        if not cpf_encontrado:
            return {"status": "CPF_NAO_ENCONTRADO_NA_BLACKLIST"}

        # Atualizar o arquivo com as linhas restantes
        if updated_lines:
            s3.put_object(Bucket=BUCKET_NAME, Key=BLACKLIST_FILE, Body='\n'.join(updated_lines).encode('utf-8'))
        else:
            # Se não houver linhas restantes, removemos o arquivo
            s3.delete_object(Bucket=BUCKET_NAME, Key=BLACKLIST_FILE)

        return {"status": "CPF_REMOVIDO_BLACKLIST"}

# Função para listar os CPFs, Motivos e Datas na blacklist
def listar_blacklist():
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=BLACKLIST_FILE)
        content = response['Body'].read().decode('utf-8')
        lista = []
        for line in content.splitlines():
            cpf, motivo, data = line.split(',')
            lista.append({"CPF": cpf, "MOTIVO": motivo, "DATA": data})
        return lista
    except s3.exceptions.NoSuchKey:
        return []

def lambda_handler(event, context):
    # Verificar o caminho do endpoint
    if 'rawPath' not in event:
        return {
            "statusCode": 400,
            "body": json.dumps({"status": "BAD_REQUEST"})
        }

    path = event['rawPath']

    # Verificar se o requestContext está presente
    method = event.get('requestContext', {}).get('http', {}).get('method', None)

    # Lidar com POST /users
    if path == "/users" and method == "POST":
        body = json.loads(event['body'])
        cpf = body.get('CPF')

        if not valida_cpf(cpf):
            return {
                "statusCode": 404,
                "body": json.dumps({"status": "CPF_INVALIDO"})
            }

        if verifica_blacklist(cpf):
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "UNABLE_TO_VOTE"})
            }
        else:
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "ABLE_TO_VOTE"})
            }

    # Lidar com GET /users para listar os CPFs na blacklist
    elif path == "/users" and method == "GET":
        lista_blacklist = listar_blacklist()
        return {
            "statusCode": 200,
            "body": json.dumps(lista_blacklist)
        }

    # Lidar com POST /blacklist
    elif path == "/blacklist" and method == "POST":
        body = json.loads(event['body'])
        cpf = body.get('CPF')
        motivo = body.get('MOTIVO')
        action = body.get('ACTION')

        if action not in ["ADD", "REMOVE"]:
            return {
                "statusCode": 400,
                "body": json.dumps({"status": "INVALID_ACTION"})
            }

        response = atualizar_blacklist(cpf, motivo, action)
        return {
            "statusCode": 200,
            "body": json.dumps(response)
        }

    return {
        "statusCode": 404,
        "body": json.dumps({"status": "NOT_FOUND"})
    }
