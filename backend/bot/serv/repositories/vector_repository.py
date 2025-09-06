import os
from pymongo import MongoClient
from dotenv import load_dotenv
from config.logger_config import get_logger
import os
import boto3
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import MongoDBAtlasVectorSearch

log = get_logger()
load_dotenv()

class MongoDBRepository:
    def __init__(self):
        self.mongodb_url = os.getenv("MONGODB_URL")
        self.db_name = os.getenv("MONGODB_DATABASE")
        self.collection_name = os.getenv("MONGODB_COLLECTION")
        self.collection_name_ = os.getenv("MONGODB_COLLECTION_IMAGES")
        
        self.bedrock = Bedrock()
        self.client =  MongoClient(self.mongodb_url)
        if not all([self.mongodb_url, self.db_name, self.collection_name]):
            raise ValueError("Faltan variables de entorno: MONGODB_URL, MONGODB_DATABASE, MONGODB_COLLECTION")
    
    def get_collection(self):
        try:
            db = self.client[self.db_name]
            return db[self.collection_name]
        except Exception as e:
            raise ValueError("Error al conectarse a Mongo: ", e)

    def get_collection_(self):
        try:
            db = self.client[self.db_name]
            return db[self.collection_name_]
        except Exception as e:
            raise ValueError("Error al conectarse a Mongo ", e)
            
    def vector_store_inference(self):
        
        vector_store = MongoDBAtlasVectorSearch(
                collection=self.get_collection(),
                embedding=self.bedrock.embedding_model(),
                text_key="content",
                index_name="vector_index"
            )
        
        return vector_store
    
class Bedrock:
    def __init__(self):
        self._aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self._aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.model = os.getenv('EMBEDDING_MODEL')
        self.model_ = os.getenv('EMBEDDING_MODEL_IMAGE')
        self._embedding_model = None
        self.bedrock_client = boto3.client(
                "bedrock-runtime",
                aws_access_key_id=self._aws_access_key,
                aws_secret_access_key=self._aws_secret_key,
                region_name="us-east-1"
            )
    def embedding_model(self):
        try:
     
            self._embedding_model = BedrockEmbeddings(
                model_id=self.model,
                client=self.bedrock_client,
                aws_access_key_id=self._aws_access_key,
                aws_secret_access_key=self._aws_secret_key,
            )
        
        except Exception as e:
            raise ValueError("Error al conectarse a Bedrock: ", e)
        return self._embedding_model 

        
    def client(self):
        try:
            return self.bedrock_client
        except Exception as e:
            raise
         