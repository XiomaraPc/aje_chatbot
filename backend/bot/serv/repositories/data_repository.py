import os
import boto3
from dotenv import load_dotenv

load_dotenv()

class DataRepository:
    def __init__(self):   
        self._endpoint_url = os.getenv('ENDPOINT_URL')
        self._dynamodb_access_key = os.getenv('DYNAMODB_ACCESS_KEY') 
        self._dynamodb_secret_access = os.getenv('DYNAMODB_SECRET_ACCESS')   
        self.dynamodb_client = None
        
    def dynamodb_cliente(self):
        try:        
            self.dynamodb_client = boto3.resource(
                service_name="dynamodb",
                region_name='us-east-1',
                aws_access_key_id=self._dynamodb_access_key,
                aws_secret_access_key=self._dynamodb_secret_access
            )
            self.table_name = os.getenv('TABLE_NAME')

            
        except Exception as e:
            raise
        return self.dynamodb_client