import json
import boto3
from typing import List, Optional, Dict

class TitanEmbeddings:
    ACCEPT = "application/json"
    CONTENT_TYPE = "application/json"
    SERVICE_NAME = 'bedrock-runtime'
    DEFAULT_REGION = 'us-east-1'
    DEFAULT_MODEL_ID = "amazon.titan-embed-text-v2:0"

    def __init__(self, model_id: str = DEFAULT_MODEL_ID, boto3_client: Optional[boto3.client] = None, region_name: str = DEFAULT_REGION):
        self.bedrock_boto3 = boto3_client or boto3.client(service_name=self.SERVICE_NAME, region_name=region_name)
        self.model_id = model_id

    def __call__(self, text: str, dimensions: int, normalize: bool = True) -> List[float]:
        """
        Returns Titan Embeddings

        Args:
            text (str): Text to embed.
            dimensions (int): Number of output dimensions.
            normalize (bool): Whether to return the normalized embedding or not.

        Returns:
            List[float]: Embedding.
        """
        body = json.dumps({
            "inputText": text,
            "dimensions": dimensions,
            "normalize": normalize
        })

        try:
            response = self.bedrock_boto3.invoke_model(
                body=body,
                modelId=self.model_id,
                accept=self.ACCEPT,
                contentType=self.CONTENT_TYPE
            )
            response_body = json.loads(response['body'].read())
            return response_body.get('embedding', [])
        except Exception as e:
            # Log the error or handle it as needed
            print(f"Error invoking model: {e}")
            return []


if __name__ == "__main__":
    titan_embeddings = TitanEmbeddings()
    embedding = titan_embeddings("Hello, world!", dimensions=256)
    print(embedding)