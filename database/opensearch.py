import boto3
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
from utils.llm import create_vector_embedding
from utils.logging import getLogger

logger = getLogger()



def get_opensearch_cluster_client(domain, host, port, opensearch_user, opensearch_password, region_name):

    auth = (opensearch_user, opensearch_password)
    if len(host) == 0:
        host = get_opensearch_endpoint(domain, region_name)

    # Create the client with SSL/TLS enabled, but hostname verification disabled.
    opensearch_client = OpenSearch(
        hosts=[{'host': host, 'port': port}],
        http_compress=True,  # enables gzip compression for request bodies
        http_auth=auth,
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False
    )
    return opensearch_client


def get_opensearch_endpoint(domain, region):
    client = boto3.client('es', region_name=region)
    response = client.describe_elasticsearch_domain(
        DomainName=domain
    )
    return response['DomainStatus']['Endpoint']


def put_bulk_in_opensearch(list, client):
 
    logger.info(f"Putting {len(list)} documents in OpenSearch")
    success, failed = bulk(client, list)
    return success, failed


def check_opensearch_index(opensearch_client, index_name):
    return opensearch_client.indices.exists(index=index_name)


def create_index(opensearch_client, index_name):
    """
    Create index
    :param opensearch_client:
    :param index_name:
    :return:
    """
    settings = {
        "settings": {
            "index": {
                "knn": True,
                "knn.space_type": "cosinesimil"
            }
        }
    }
    response = opensearch_client.indices.create(index=index_name, body=settings)
    return bool(response['acknowledged'])


def create_index_mapping(opensearch_client, index_name, dimension):
    """
    Create index mapping
    :param opensearch_client:
    :param index_name:
    :param dimension:
    :return:
    """
    response = opensearch_client.indices.put_mapping(
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


def delete_opensearch_index(opensearch_client, index_name):
    logger.info(f"Trying to delete index {index_name}")
    try:
        response = opensearch_client.indices.delete(index=index_name)
        logger.info(f"Index {index_name} deleted")
        return response['acknowledged']
    except Exception as e:
        logger.info(f"Index {index_name} not found, nothing to delete")
        return True


def retrieve_results_from_opensearch(index_name, region_name, domain, opensearch_user, opensearch_password,
                                     query_embedding, top_k=3, host='', port=443, profile_name=None):
    opensearch_client = get_opensearch_cluster_client(domain, host, port, opensearch_user, opensearch_password, region_name)
    search_query = {
        "size": top_k,  # Adjust the size as needed to retrieve more or fewer results
        "query": {
            "bool": {
                "filter": {
                    "match_phrase": {
                        "profile": profile_name
                    }
                },
                "must": [
                    {
                        "knn": {
                            "vector_field": {  # Make sure 'vector_field' is the name of your vector field in OpenSearch
                                "vector": query_embedding,
                                "k": top_k  # Adjust k as needed to retrieve more or fewer nearest neighbors
                            }
                        }
                    }
                ]
            }

        }
    }

    # Execute the search query
    response = opensearch_client.search(
        body=search_query,
        index=index_name
    )

    return response['hits']['hits']


def opensearch_index_init(opensearch_info):
    """
    OpenSearch index init
    :return:
    """

    opensearch_info = {}
    try:
        auth = (opensearch_info["username"], opensearch_info["password"])
        host = opensearch_info["host"]
        port = opensearch_info["port"]
        # Create the client with SSL/TLS enabled, but hostname verification disabled.
        opensearch_client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_compress=True,  # enables gzip compression for request bodies
            http_auth=auth,
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False
        )
        index_name =  "text_neptune"
        dimension = opensearch_info['embedding_dimension']
        index_create_success = True
        exists = check_opensearch_index(opensearch_client, index_name)
        if not exists:
            logger.info("Creating OpenSearch index")
            success = create_index(opensearch_client, index_name)
            if success:
                success = create_index_mapping(opensearch_client, index_name, dimension)
                logger.info(f"OpenSearch Index mapping created")
            else:
                index_create_success = False
        return index_create_success
    except Exception as e:
        logger.error("create index error")
        logger.error(e)
        return False



def put_bulk_in_opensearch(list, client):
    logger.info(f"Putting {len(list)} documents in OpenSearch")
    success, failed = bulk(client, list)
    return success, failed

class OpenSearchDao:

    def __init__(self, host, port, opensearch_user, opensearch_password):
        auth = (opensearch_user, opensearch_password)

        # Create the client with SSL/TLS enabled, but hostname verification disabled.
        self.opensearch_client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_compress=True,  # enables gzip compression for request bodies
            http_auth=auth,
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False
        )

    def retrieve_samples(self, index_name, profile_name):
        # search all docs in the index filtered by profile_name
        search_query = {
            "sort": [
                {
                    "_score": {
                        "order": "desc"
                    }
                }
            ],
            "_source": {
                "includes": ["text", "answer"]
            },
            "size": 5000,
            "query": {
                "bool": {
                    "must": [],
                    "filter": [
                        {
                            "match_all": {}
                        },
                        {
                            "match_phrase": {
                                "profile": profile_name
                            }
                        }
                    ],
                    "should": [],
                    "must_not": []
                }
            }
        }

        # Execute the search query
        response = self.opensearch_client.search(
            body=search_query,
            index=index_name
        )

        return response['hits']['hits']


    def add_sample(self, index_name, profile_name, text, answer, embedding):
        record = {
            '_index': index_name,
            'text': text,
            'answer': answer,
            'profile': profile_name,
            'vector_field': embedding
        }

        success, failed = put_bulk_in_opensearch([record], self.opensearch_client)
        return success == 1



    def delete_sample(self, index_name, profile_name, doc_id):
        return self.opensearch_client.delete(index=index_name, id=doc_id)

    def search_sample(self, profile_name, top_k, index_name, query):
        records_with_embedding = create_vector_embedding(query, index_name=index_name)
        return self.search_sample_with_embedding(profile_name, top_k, index_name,  records_with_embedding['vector_field'])


    def search_sample_with_embedding(self, profile_name, top_k, index_name, query_embedding):
        search_query = {
            "size": top_k,  # Adjust the size as needed to retrieve more or fewer results
            "query": {
                "bool": {
                    "filter": {
                        "match_phrase": {
                            "profile": profile_name
                        }
                    },
                    "must": [
                        {
                            "knn": {
                                "vector_field": {
                                    # Make sure 'vector_field' is the name of your vector field in OpenSearch
                                    "vector": query_embedding,
                                    "k": top_k  # Adjust k as needed to retrieve more or fewer nearest neighbors
                                }
                            }
                        }
                    ]
                }

            }
        }

        # Execute the search query
        response = self.opensearch_client.search(
            body=search_query,
            index=index_name
        )

        return response['hits']['hits']
