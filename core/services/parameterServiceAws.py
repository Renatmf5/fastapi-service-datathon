from fastapi import HTTPException
import boto3

# Função para obter parâmetros do SSM Parameter Store
def get_ssm_parameter(name: str) -> str:
    ssm_client = boto3.client('ssm', region_name='us-east-1')
    try:
        response = ssm_client.get_parameter(Name=name, WithDecryption=True)
        return response['Parameter']['Value']
    except ssm_client.exceptions.ParameterNotFound:
        raise HTTPException(status_code=500, detail=f"Parameter {name} not found in SSM Parameter Store")
