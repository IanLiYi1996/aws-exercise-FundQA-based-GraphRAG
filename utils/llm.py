import os
import json
import boto3
import logging
import pandas as pd
from botocore.config import Config
from botocore.exceptions import ClientError


config = Config(
    region_name=os.getenv('BEDROCK_REGION'),
    signature_version='v4',
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    },
    read_timeout=600
)

embedding_info = {
    "embedding_platform": os.getenv('EMBEDDING_PLATFORM', "bedrock"),
    "embedding_name": os.getenv('EMBEDDING_NAME', "amazon.titan-embed-text-v2:0"),
    "embedding_dimension": int(os.getenv('EMBEDDING_DIMENSION', 256)),
    "embedding_region": os.getenv('EMBEDDING_REGION', os.getenv('AWS_DEFAULT_REGION'))
}

BEDROCK_SECRETS_AK_SK = os.getenv('BEDROCK_SECRETS_AK_SK', '')

def get_bedrock_parameter():
    bedrock_ak_sk_info = {}
    try:
        session = boto3.session.Session()
        sm_client = session.client(service_name='secretsmanager', region_name=os.getenv('AWS_DEFAULT_REGION'))
        if BEDROCK_SECRETS_AK_SK is not None and BEDROCK_SECRETS_AK_SK != "":
            bedrock_info = sm_client.get_secret_value(SecretId=BEDROCK_SECRETS_AK_SK)['SecretString']
            data = json.loads(bedrock_info)
            access_key = data.get('access_key_id')
            secret_key = data.get('secret_access_key')
            bedrock_ak_sk_info['access_key_id'] = access_key
            bedrock_ak_sk_info['secret_access_key'] = secret_key
        else:
            return bedrock_ak_sk_info
    except ClientError as e:
        logging.error(e)
    return bedrock_ak_sk_info


bedrock_ak_sk_info = get_bedrock_parameter()


def get_bedrock_client():
    global bedrock
    if not bedrock:
        if len(bedrock_ak_sk_info) == 0:
            bedrock = boto3.client(service_name='bedrock-runtime', config=config)
        else:
            bedrock = boto3.client(
                service_name='bedrock-runtime', config=config,
                aws_access_key_id=bedrock_ak_sk_info['access_key_id'],
                aws_secret_access_key=bedrock_ak_sk_info['secret_access_key'])
    return bedrock

def create_vector_embedding(text, index_name):
    model_name = embedding_info["embedding_name"]
    if embedding_info["embedding_platform"] == "bedrock":
        return create_vector_embedding_with_bedrock(text, index_name, model_name)
    else:
        return []


def create_vector_embedding_with_bedrock(text, index_name, model_name):
    payload = {"inputText": f"{text}"}
    body = json.dumps(payload)
    modelId = model_name
    accept = "application/json"
    contentType = "application/json"

    response = get_bedrock_client().invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())

    embedding = response_body.get("embedding")
    return {"_index": index_name, "text": text, "vector_field": embedding}