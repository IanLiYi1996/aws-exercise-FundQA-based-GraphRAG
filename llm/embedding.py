import json
import boto3

class TitanEmbeddings(object):
    accept = "application/json"
    content_type = "application/json"

    def __init__(self, model_id="amazon.titan-embed-text-v2:0", boto3_client=None, region_name='us-east-1'):

        if boto3_client:
            self.bedrock_boto3 = boto3_client
        else:
            # self.bedrock_boto3 = boto3.client(service_name='bedrock-runtime')
            self.bedrock_boto3 = boto3.client(
                service_name='bedrock-runtime', 
                region_name=region_name, 
            )
        self.model_id = model_id

    def __call__(self, text, dimensions, normalize=True):
        """
        Returns Titan Embeddings

        Args:
            text (str): text to embed
            dimensions (int): Number of output dimensions.
            normalize (bool): Whether to return the normalized embedding or not.

        Return:
            List[float]: Embedding

        """

        body = json.dumps({
            "inputText": text,
            "dimensions": dimensions,
            "normalize": normalize
        })

        response = self.bedrock_boto3.invoke_model(
            body=body, modelId=self.model_id, accept=self.accept, contentType=self.content_type
        )

        response_body = json.loads(response.get('body').read())

        return response_body['embedding']