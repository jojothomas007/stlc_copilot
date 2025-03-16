import faiss
import numpy
import openai
import os
import json
import logging
import base64
from typing import List
import requests
from requests.auth import HTTPBasicAuth
from src.stlc_copilot.config import Config
from src.stlc_copilot.utils.request_sender import RequestSender
from requests.exceptions import HTTPError, RequestException

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class SearchService:

    def __init__(self):
        self.__openai:openai = openai
        self.__openai.api_key = Config.gpt_api_key # Ensure API key is set as an environment variable
        self.__embedding_model = "text-embedding-ada-002"
        
    def __chunk_text(self, text, chunk_size=512, overlap=100):
        """Chunks text into smaller overlapping segments."""
        if overlap >= chunk_size:
            raise ValueError("Overlap must be smaller than chunk_size to avoid infinite loop.")
        
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start = start + chunk_size - overlap  # Ensure forward progression
        return chunks

    def __embed_text_openai(self, chunks):
        """Embeds text chunks using OpenAI's embeddings API."""
        embeddings = []
        for chunk in chunks:
            response = self.__openai.embeddings.create(input=[chunk], model=self.__embedding_model)
            embeddings.append(response.data[0].embedding)
        return embeddings

    def __build_faiss_index(self, embeddings):
        """Builds a FAISS index from embeddings."""
        d = len(embeddings[0])  # Dimension of embeddings
        index = faiss.IndexFlatL2(d)
        index.add(numpy.array(embeddings).astype('float32'))
        return index

    def search_text(self, text:str, query:str, k:int=5):
        if not self.__openai.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        chunks = self.__chunk_text(text)
        embeddings = self.__embed_text_openai(chunks)
        index = self.__build_faiss_index(embeddings)
        query_embedding_response = self.__openai.embeddings.create(input=[query], model=self.__embedding_model)
        query_embedding = query_embedding_response.data[0].embedding
        D, I = index.search(numpy.array([query_embedding]).astype('float32'), k)
        results = [(chunks[i], D[0][idx]) for idx, i in enumerate(I[0])]
        contents:str = " "
        if results:
            contents = "\n".join([chunk for chunk, _ in results]) #extract only the chunks
        return contents
