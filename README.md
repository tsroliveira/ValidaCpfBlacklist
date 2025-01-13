# CPF Blacklist API

Esta é uma aplicação serverless em Python que utiliza AWS Lambda e Amazon S3 para gerenciar uma lista de CPFs bloqueados (blacklist). A aplicação permite a validação de CPFs, consulta de status de bloqueio e adição ou remoção de CPFs da blacklist. O sistema está implementado como uma função Lambda com URL externa, sem segurança adicional habilitada.

## Funcionalidades

1. **Validação de CPF**: Verifica se o CPF é válido conforme as regras brasileiras.
2. **Verificação de blacklist**: Consulta um arquivo CSV no S3 para verificar se um CPF está na blacklist.
3. **Atualização da blacklist**: Adiciona ou remove CPFs da blacklist, registrando o motivo e a data.
4. **Listagem de CPFs na blacklist**: Retorna a lista de CPFs na blacklist, juntamente com o motivo e a data.

## Requisitos

- AWS CLI configurado
- AWS Lambda
- Amazon S3
- Python 3.x
- Boto3 (SDK AWS para Python)

## Passos para Configuração

### 1. Configuração do S3

1. Acesse o [Amazon S3](https://s3.console.aws.amazon.com/s3) e crie um bucket com o nome `cpfblacklist`.
2. No bucket criado, adicione um arquivo chamado `blacklist.csv` (caso o arquivo ainda não exista, ele será criado pela função Lambda automaticamente).
   
### 2. Configuração da Função Lambda

1. No console da AWS, navegue até o [AWS Lambda](https://console.aws.amazon.com/lambda).
2. Crie uma nova função Lambda com runtime Python 3.x.
3. No código da função Lambda, adicione o código do script Python responsável pela validação e manipulação de CPFs na blacklist.
4. Configure as permissões da função Lambda para permitir leitura e escrita no bucket S3 (`cpfblacklist`).

### 3. Configuração de API Gateway

1. No console da AWS, vá para o [API Gateway](https://console.aws.amazon.com/apigateway).
2. Crie uma nova API REST e configure os endpoints:
   - **POST** `/users`: Para validar se o CPF pode votar.
   - **POST** `/blacklist`: Para adicionar ou remover CPFs da blacklist.
   - **GET** `/users`: Para listar todos os CPFs, motivos e datas da blacklist.

3. Conecte os endpoints ao Lambda que você criou.
4. Habilite a integração com o Lambda e defina as respostas HTTP conforme o projeto.

### 4. Deploy

1. Realize o deploy da API no API Gateway.
2. Copie a URL gerada pela API e teste os endpoints utilizando ferramentas como Postman ou CURL.

## Exemplo de Requisições

### Validação de CPF

**POST /users**

```json
{
    "CPF": "98765432101"
}
```
Resposta:
```json
{
    "status": "ABLE_TO_VOTE"
}
```
Adicionar CPF à Blacklist
POST /blacklist

```json
{
    "CPF": "98765432101",
    "MOTIVO": "Fraude",
    "ACTION": "ADD"
}
```
Resposta:

```json
{
    "status": "CPF_ADICIONADO_BLACKLIST"
}
```
Remover CPF da Blacklist
POST /blacklist

```json
{
    "CPF": "98765432101",
    "ACTION": "REMOVE"
}
```
Resposta:

```json
{
    "status": "CPF_REMOVIDO_BLACKLIST"
}
```
Listar CPFs da Blacklist
GET /users

Resposta:

```json
[
    {
        "CPF": "98765432101",
        "MOTIVO": "Fraude",
        "DATA": "2025-01-30 11:00:00"
    }
]
```
Permissões AWS
As permissões a seguir são necessárias para que a função Lambda possa acessar o bucket S3:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::cpfblacklist/*"
        }
    ]
}
```

Contribuição
Sinta-se à vontade para abrir issues e enviar pull requests para melhorias neste projeto.

Licença
Este projeto está licenciado sob a MIT License.

```javascript
Esse `README.md` contém todas as instruções básicas para configurar o projeto, além de exemplos
de uso da API, configuração do bucket S3, e permissões necessárias no AWS Lambda.

