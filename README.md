# aws-exercise-FundQA-based-GraphRAG

## Introduction

A  demo using Amazon Bedrock, Amazon OpenSearch, Amazon Neptune Graph Database with GraphRAG technique.

### 架构图



### 实现功能



### Demo展示 

<video src='./assets/demo.mp4' controls width="180"></video>

<br/>  <!-- 添加换行符以确保后续内容显示 -->


### 项目结构
```
aws-exercise-FundQA-based-GraphRA
├── Dockerfile 项目打包镜像脚本
├── README.md
├── assets 存放相关资源
├── config_files 存放项目配置信息
│   ├── aws_config.yaml
│   ├── llm_prompt.py
│   └── stauth_config.yaml
├── core 核心流程实现
│   └── chat_service.py
├── data_example 示例数据
│   ├── edge.csv
│   ├── vertex.csv
│   └── vertex2.csv
├── database AWS数据服务
│   ├── neptune.py
│   └── opensearch.py
├── llm AWS Bedrock调用
│   ├── embedding.py
│   └── llm.py
├── main.py 项目入口
├── notebooks 相关notebook文件
│   ├── Titan-V2-Embeddings.ipynb
│   ├── bedrock_invoke.ipynb
│   ├── graph_rag.ipynb
│   ├── inser_data_in_neptune.ipynb
│   ├── insert_embeddding_into_opensearch.ipynb
│   ├── llama_index.ipynb
│   └── neptune-connect.ipynb
├── pages chat页面实现
│   └── chat.py
├── requirements.txt 相关依赖
└── utils 工具资源
    ├── llm.py
    ├── logging.py
    └── pages_config.py
```

### TODO:

1. 用无服务的架构- 升级ECS托管服务
2. 前置加上ELB负载均衡,认证换成Cognito
3. 密钥存储服务后续换成Amazon Secret Manager
4. 尽量都选用Serverless的架构


### 构建过程



### 过程遇到难点及解决方式



