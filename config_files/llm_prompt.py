SYSTEM_PROMPT = '''You are a helpful chatbot.'''

CYPHER_GENERATION_PROMPT = '''Create a **Amazon Neptune flavor Cypher query** based on provided relationship paths and a question.
The query should be able to try best answer the question with the given graph schema.
The query should follow the following guidance:
- Fully qualify property references with the node's label.
```
// Incorrect
MATCH (p:person)-[:follow]->(:person) RETURN p.name
// Correct
MATCH (p:person)-[:follow]->(i:person) RETURN i.name
```
- Strictly follow the relationship on schema:
Given the relationship ['(:`Art`)-[:`BY_ARTIST`]->(:`Artist`)']:
```
// Incorrect
MATCH (a:Artist)-[:BY_ARTIST]->(t:Art)
RETURN DISTINCT t
// Correct
MATCH (a:Art)-[:BY_ARTIST]->(t:Artist)
RETURN DISTINCT t
```
- Follow single direction (from left to right) query model:
```
// Incorrect
MATCH (a:Artist)<-[:BY_ARTIST]-(t:Art)
RETURN DISTINCT t
// Correct
MATCH (a:Art)-[:BY_ARTIST]->(t:Artist)
RETURN DISTINCT t
```
Given any relationship property, you should just use them following the relationship paths provided, respecting the direction of the relationship path.
With these information, construct a Amazon Neptune Cypher query to provide the necessary information for answering the question, only return the plain text query, no explanation, apologies, or other text.
NOTE:
0. Try to get as much graph data as possible to answer the question
1. Put a limit of 30 results in the query.
---
Schema: 
Vertex: FundManager,Fund
Rel: manage.from(FundManager).to(Fund)

---
---
Question: {user_input}

Amazon Neptune flavor Query:''' 

RESULT_GENERSTION_PROMPT = '''Create a fund analysis response based on the provided information and guidelines. The response should be structured clearly and written in the first person. Please adhere to the following requirements:

Ensure all statements are based on the provided information without fabricating any content.

// Incorrect
I think the fund is good, and you should invest.
// Correct
Based on my analysis, I recommend considering this fund for investment due to its strong fundamentals.
With this information, construct a well-structured response that addresses the inquiry, only return the plain text response, no explanations, apologies, or additional text.

NOTE:
0. Aim to provide a comprehensive analysis based on the data available.

Keep the response within a limit of 300 words.
graph_result: {graph_result}
embedding_result: {embedding_result}
Question: {user_input}

Final Response: '''