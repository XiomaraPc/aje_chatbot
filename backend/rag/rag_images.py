import os
import json
import base64
from pathlib import Path
from connection import MongoDB, Bedrock

class RagImages:
    def __init__(self):
        self.IMAGES_FOLDER = "./images"
        self.bedrock = Bedrock()
        self.mongo = MongoDB()
        self.collection = self.mongo.get_collection_()
        self.bedrock = self.bedrock.client()
        self.model_id = "amazon.titan-embed-image-v1"

    def image_to_base64(self, image_path: str):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def embed_image(self, image_path: str):
        image_base64 = self.image_to_base64(image_path)
        resp = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=json.dumps({
                "inputImage": image_base64,
                "embeddingConfig": {"outputEmbeddingLength": 1024}
            }),
            contentType="application/json"
        )
        body = json.loads(resp["body"].read())
        return body["embedding"]

    def get_image_files(self):
        image_extensions = ['.png', '.jpg', '.jpeg']
        image_files = []
        
        for root, dirs, files in os.walk(self.IMAGES_FOLDER):
            for file in files:
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    image_files.append(os.path.join(root, file))
        
        return image_files

    def insert_image_embedding(self, image_path: str):
        """Insertar embedding de imagen en MongoDB"""
        try:
            embedding = self.embed_image(image_path)
            
            file_name = Path(image_path).stem
            product_name = file_name.replace('_', ' ').title()
            
            document = {
                "embedding": embedding,
                "product_name": product_name,
                "file_name": file_name,
                "content_type": "image",
                "source": "aje_products"
            }
            
            self.collection.insert_one(document)
            print(f"Insertada: {product_name}")
            
        except Exception as e:
            print(f"Error insertando {image_path}: {str(e)}")

    def insert(self):
        image_files = self.get_image_files()
        
        if not image_files:
            print("No se encontraron imágenes")
            return
        
        processed = 0
        
        for image_path in image_files:
            self.insert_image_embedding(image_path)
            processed += 1
        
        print(f"Total insertadas: {processed} imágenes")

if __name__ == "__main__":
    processor = RagImages()
    print("Insertando imágenes de productos AJE...")
    processor.insert()