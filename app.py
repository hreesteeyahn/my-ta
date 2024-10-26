from flask import Flask, request, render_template, jsonify
import requests
from datasets import load_dataset
from haystack import Document
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.builders import PromptBuilder
from haystack.components.generators import HuggingFaceAPIGenerator
from haystack.components.generators.utils import print_streaming_chunk
from haystack.utils import Secret
from haystack import Pipeline


API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-1B-Instruct"
API_TOKEN = "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"


### HAYSTACK
document_store = InMemoryDocumentStore()

# dataset = load_dataset("bilgeyucel/seven-wonders", split="train")
# docs = [Document(content=doc["content"], meta=doc["meta"]) for doc in dataset]
docs = [Document(content="Paris is the capital of France."),
        Document(content="Berlin is the capital of Germany."),
        Document(content="Rome is the capital of Italy."),
        Document(content="Madrid is the capital of Spain.")]

doc_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
doc_embedder.warm_up()

docs_with_embeddings = doc_embedder.run(docs)
document_store.write_documents(docs_with_embeddings["documents"])

text_embedder = SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
retriever = InMemoryEmbeddingRetriever(document_store)


template = """
Given the following information, answer the question.

Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{question}}
Answer:
"""

prompt_builder = PromptBuilder(template=template)

generator = HuggingFaceAPIGenerator(api_type="inference_endpoints",
                                    api_params={"url": API_URL},
                                    token=Secret.from_token(API_TOKEN),
                                    streaming_callback=print_streaming_chunk)

rag_pipeline = Pipeline()
# Add components to your pipeline
rag_pipeline.add_component("text_embedder", text_embedder)
rag_pipeline.add_component("retriever", retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.add_component("llm", generator)

# Now, connect the components to each other
rag_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
rag_pipeline.connect("retriever", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder", "llm")

# question = "What does Rhodes Statue look like?"
# response = basic_rag_pipeline.run({"text_embedder": {"text": question}, "prompt_builder": {"question": question}})
# print(response['llm']['replies'][0])


### FLASK
app = Flask(__name__)

headers = {"Authorization": "Bearer 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"}

@app.route("/")
def home():
    return render_template("editor.html", response="")

@app.route("/submit", methods=["POST"])
def submit():
    # Get the JSON data from the request
    data = request.get_json()  # Use get_json() to parse JSON body
    user_input = data.get("userInput")  # Get the input from the request
    
    # # Prepare the payload with return_full_text set to False
    # payload = {
    #     "inputs": user_input,
    #     "parameters": {
    #         "return_full_text": False  # Set return_full_text to False
    #     }
    # }

    # # Make the API request
    # response = requests.post(API_URL, headers=headers, json=payload)
    # api_response = response.json()

    # # Render the HTML page with the response from the API
    # return render_template("inference.html", response=api_response[0]['generated_text'])
    
    # Run the RAG pipeline
    response = rag_pipeline.run({"text_embedder": {"text": user_input}, "prompt_builder": {"question": user_input}})

    # Extract the generated response
    generated_text = response['llm']['replies'][0] if response['llm']['replies'][0] else "No relevant information found."
    # print(generated_text)

    # Return the generated text as a JSON response
    return jsonify({"response": generated_text})
    # # # Render the HTML page with the response from the API
    # return render_template("editor.html", response=generated_text)

if __name__ == "__main__":
    app.run()
