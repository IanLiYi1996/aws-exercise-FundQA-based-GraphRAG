import boto3
import json
import logging
from botocore.config import Config

class BedrockLLMClient:
    def __init__(self, region_name="us-east-1"):
        self.config = Config(
            region_name=region_name,
            signature_version='v4',
            retries={
                'max_attempts': 10,
                'mode': 'standard'
            },
            read_timeout=600
        )
        self.bedrock = None

    def get_bedrock_client(self):
        if not self.bedrock:
            self.bedrock = boto3.client(service_name='bedrock-runtime', config=self.config)
        return self.bedrock

    def invoke_llama_70b(self, model_id, system_prompt, user_prompt, max_tokens=2048, with_response_stream=False):
        """
        Invoke LLama-70B model
        :param model_id: The ID of the model to use
        :param system_prompt: The system prompt
        :param user_prompt: The user prompt
        :param max_tokens: Maximum number of tokens to generate (default: 2048)
        :param with_response_stream: Whether to use response streaming (default: False)
        :return: The model's response
        """
        try:
            llama3_prompt = """
            <|begin_of_text|><|start_header_id|>system<|end_header_id|>

            {system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

            {user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
            """
            body = {
                "prompt": llama3_prompt.format(system_prompt=system_prompt, user_prompt=user_prompt),
                "max_gen_len": max_tokens,
                "temperature": 0.01,
                "top_p": 0.9
            }

            if with_response_stream:
                response = self.get_bedrock_client().invoke_model_with_response_stream(body=json.dumps(body), modelId=model_id)
                return response
            else:
                response = self.get_bedrock_client().invoke_model(
                    modelId=model_id, body=json.dumps(body)
                )
                response_body = json.loads(response["body"].read())
                return response_body
        except Exception as e:
            logging.error("Couldn't invoke LLama 70B")
            logging.error(e)
            raise

if __name__ == "__main__":
    client = BedrockLLMClient()
    response = client.invoke_llama_70b(
        model_id="meta.llama3-70b-instruct-v1:0",
        system_prompt="You are a friendly conversation assistant",
        user_prompt="who are you"
    )
    print(response)