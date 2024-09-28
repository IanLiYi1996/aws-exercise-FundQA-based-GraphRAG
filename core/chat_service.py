import yaml
import json
from yaml.loader import SafeLoader
from database.neptune import NeptuneGraphDB
from database.opensearch import OpenSearchDao
from llm.embedding import TitanEmbeddings
from llm.llm import BedrockLLMClient
from config_files.llm_prompt import *

class ChatService:
    def __init__(self):
        try:
            self.aws_config = self.load_aws_config('config_files/aws_config.yaml')
            self.neptune_db = NeptuneGraphDB(self.aws_config['neptune_info']['neptune_endpoint'])
            self.opensearch_dao = OpenSearchDao(
                host=self.aws_config['opensearch_info']["host"],
                port=self.aws_config['opensearch_info']["port"],
                opensearch_user=self.aws_config['opensearch_info']["username"],
                opensearch_password=self.aws_config['opensearch_info']["password"]
            )
            self.titan_embeddings = TitanEmbeddings()
            self.bedrock_llm_client = BedrockLLMClient()
        except Exception as e:
            print(f"Error initializing ChatService: {e}")
            raise

    @staticmethod
    def load_aws_config(file_path: str) -> dict:
        try:
            with open(file_path) as file:
                return yaml.load(file, Loader=SafeLoader)
        except FileNotFoundError:
            print(f"Configuration file not found: {file_path}")
            raise
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            raise

    def generate_llm_response(self, model_id: str, system_prompt: str, user_prompt: str) -> str:
        try:
            return self.bedrock_llm_client.invoke_llama_70b(model_id=model_id, system_prompt=system_prompt, user_prompt=user_prompt)['generation']
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            raise

    def execute_chat(self, user_input: str) -> str:
        try:
            model_id = self.aws_config['bedrock_info']["llama_model_id"]

            # Generate Cypher query using LLM
            cypher_query = self.generate_llm_response(
                model_id=model_id,
                system_prompt=SYSTEM_PROMPT,
                user_prompt=CYPHER_GENERATION_PROMPT.format_map({'user_input':user_input})
            )
            graph_result = self.neptune_db.execute_opencypher_query(cypher_query)
            formatted_graph_result = json.dumps(graph_result, indent=2)

            # Generate embedding and search using OpenSearch
            input_embedding = self.titan_embeddings(user_input, dimensions=256)
            embedding_result = self.opensearch_dao.search_sample_with_embedding('profile1', 1, 'text_neptune', input_embedding)[0]['_source']['answer']

            # Generate final response using LLM
            response = self.generate_llm_response(
                model_id=model_id,
                system_prompt=SYSTEM_PROMPT,
                user_prompt=RESULT_GENERSTION_PROMPT.format_map({'graph_result': formatted_graph_result, 'embedding_result': embedding_result, 'user_input':user_input})
            )

            return response
        except Exception as e:
            print(f"Error executing chat: {e}")
            return "An error occurred while processing your request."

# Example usage
if __name__ == "__main__":
    chat_service = ChatService()
    user_input = "介绍一下张坤和他管理的基金都有哪些?"
    response = chat_service.execute_chat(user_input)
    print("Chat response:", response)
