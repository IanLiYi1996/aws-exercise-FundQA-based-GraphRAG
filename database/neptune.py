import requests
import json

class NeptuneGraphDB:
    def __init__(self, endpoint, port=8182):
        self.endpoint = endpoint
        self.port = port
        self.url = f'https://{self.endpoint}:{self.port}/openCypher'  # 使用 HTTPS 和指定的路径

    def execute_opencypher_query(self, query):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'  # 设置内容类型为表单
        }
        payload = {
            'query': query  # 使用表单数据格式发送查询
        }
        
        response = requests.post(self.url, headers=headers, data=payload, verify=False)  # verify=False 用于忽略 SSL 证书验证

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Query failed with status code {response.status_code}: {response.text}")

# 使用示例
if __name__ == "__main__":
    neptune_endpoint = 'db-neptune-1.cluster-ro-c54gq640s2vk.us-east-1.neptune.amazonaws.com'  # 示例端点
    neptune_db = NeptuneGraphDB(neptune_endpoint)
    cypher_query = "MATCH (n1) RETURN n1;"  # 替换为您的 OpenCypher 查询

    try:
        result = neptune_db.execute_opencypher_query(cypher_query)
        print("Query Result:", json.dumps(result, indent=2))
    except Exception as e:
        print("Error:", e)
