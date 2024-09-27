import boto3
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
from utils.llm import create_vector_embedding
from utils.logging import getLogger

logger = getLogger()

class OpenSearchInitializer:
    def __init__(self, opensearch_info):
        self.opensearch_info = opensearch_info
        self.client = self._create_client()

    def _create_client(self):
        auth = (self.opensearch_info["username"], self.opensearch_info["password"])
        host = self.opensearch_info["host"]
        port = self.opensearch_info["port"]

        return OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_compress=True,
            http_auth=auth,
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False
        )

    def initialize_index(self):
        index_name = "text_neptune"
        dimension = self.opensearch_info['embedding_dimension']
        
        if not self._check_index_exists(index_name):
            logger.info("Creating OpenSearch index")
            if self._create_index(index_name) and self._create_index_mapping(index_name, dimension):
                logger.info("OpenSearch Index mapping created")
                return True
        return False

    def _check_index_exists(self, index_name):
        return self.client.indices.exists(index=index_name)

    def _create_index(self, index_name):
        settings = {
            "settings": {
                "index": {
                    "knn": True,
                    "knn.space_type": "cosinesimil"
                }
            }
        }
        response = self.client.indices.create(index=index_name, body=settings)
        return bool(response['acknowledged'])

    def _create_index_mapping(self, index_name, dimension):
        response = self.client.indices.put_mapping(
            index=index_name,
            body={
                "properties": {
                    "vector_field": {
                        "type": "knn_vector",
                        "dimension": dimension
                    },
                    "text": {
                        "type": "keyword"
                    },
                    "profile": {
                        "type": "keyword"
                    }
                }
            }
        )
        return bool(response['acknowledged'])

class OpenSearchDao:
    def __init__(self, host, port, opensearch_user, opensearch_password):
        self.client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_compress=True,
            http_auth=(opensearch_user, opensearch_password),
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False
        )

    def retrieve_samples(self, index_name, profile_name):
        search_query = {
            "sort": [{"_score": {"order": "desc"}}],
            "_source": {"includes": ["text", "answer"]},
            "size": 5000,
            "query": {
                "bool": {
                    "filter": [
                        {"match_phrase": {"profile": profile_name}}
                    ]
                }
            }
        }
        response = self.client.search(body=search_query, index=index_name)
        return response['hits']['hits']

    def add_sample(self, index_name, profile_name, text, answer, embedding):
        record = {
            '_index': index_name,
            'text': text,
            'answer': answer,
            'profile': profile_name,
            'vector_field': embedding
        }
        success, failed = bulk(self.client, [record])
        return success == 1

    def delete_sample(self, index_name, doc_id):
        return self.client.delete(index=index_name, id=doc_id)

    def search_sample(self, profile_name, top_k, index_name, query):
        records_with_embedding = create_vector_embedding(query, index_name=index_name)
        return self.search_sample_with_embedding(profile_name, top_k, index_name, records_with_embedding['vector_field'])

    def search_sample_with_embedding(self, profile_name, top_k, index_name, query_embedding):
        search_query = {
            "size": top_k,
            "query": {
                "bool": {
                    "filter": {"match_phrase": {"profile": profile_name}},
                    "must": [{
                        "knn": {
                            "vector_field": {
                                "vector": query_embedding,
                                "k": top_k
                            }
                        }
                    }]
                }
            }
        }
        response = self.client.search(body=search_query, index=index_name)
        return response['hits']['hits']


if __name__ == "__main__":
    # 假设我们有以下的 OpenSearch 连接信息
    opensearch_info = {
        "username": "your_username",
        "password": "your_password",
        "host": "your_host",
        "port": 443,
        "embedding_dimension": 128  # 假设嵌入维度为128
    }

    # 初始化 OpenSearch 索引
    initializer = OpenSearchInitializer(opensearch_info)
    if initializer.initialize_index():
        logger.info("OpenSearch index initialized successfully.")
    else:
        logger.error("Failed to initialize OpenSearch index.")

    # 使用 OpenSearchDao 进行数据操作
    dao = OpenSearchDao(opensearch_info["host"], opensearch_info["port"], opensearch_info["username"], opensearch_info["password"])

    # 添加样本
    success = dao.add_sample("text_neptune", "profile1", "Sample text", "Sample answer", [0.1] * 128)
    if success:
        logger.info("Sample added successfully.")
    else:
        logger.error("Failed to add sample.")

    # 检索样本
    samples = dao.retrieve_samples("text_neptune", "profile1")
    logger.info(f"Retrieved samples: {samples}")

    # 删除样本
    dao.delete_sample("text_neptune", "sample_doc_id")  # 替换为实际的文档 ID
    logger.info("Sample deleted.")
