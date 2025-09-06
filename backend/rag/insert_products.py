import re
import json
from unidecode import unidecode
from langchain.docstore.document import Document
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from connection import MongoDB, Bedrock

class RagProducts:
    def __init__(self):
        self.PRODUCTS_JSON = "./docs/database.json"
        self.bedrock = Bedrock()
        self.mongo = MongoDB()
        self.embedding_model = self.bedrock.embedding_model()
        self.collection = self.mongo.mongo_client()

    def load_products_json(self):
        """Cargar productos del archivo JSON"""
        with open(self.PRODUCTS_JSON, 'r', encoding='utf-8') as f:
            products_data = json.load(f)
        return products_data["productos"]

    def remove_accents(self, text):
        return unidecode(text)

    def normalize_text(self, text):
        text = text.lower()
        text = text.replace("\n", " ")
        text = re.sub(r"\s+", " ", text).strip()
        text = self.remove_accents(text)
        return text

    def create_product_text(self, producto):
        """Crear texto descriptivo completo del producto"""
        product_text = f"""
        PRODUCTO: {producto['nombre']} {producto['sabor']} {producto.get('tamaño', '')}
        
        Información del producto:
        - Nombre: {producto['nombre']}
        - Sabor: {producto['sabor']}
        - Tipo: {producto['tipo']}
        - Tamaño: {producto.get('tamaño', 'No especificado')}
        - Categoría: {producto['categoria']}
        
        Descripción: {producto['descripcion']}
        Países donde se vende: {', '.join(producto['pais_venta'])}
        Mensaje comercial: {producto['mensaje_comercial']}
        Ingredientes: {producto['ingredientes']}
        Beneficios: {', '.join(producto['beneficios'])}

        """
        
        return product_text

    def insert(self):
        productos = self.load_products_json()
    
        all_documents = []
        
        for producto in productos:
            product_text = self.create_product_text(producto)
            
            product_doc = Document(
                page_content=product_text,
                metadata={
                    "source": "productos_aje",
                    "producto_id": producto["id"],
                    "producto_nombre": producto["nombre"],
                    "producto_sabor": producto["sabor"],
                    "producto_tipo": producto["tipo"],
                    "producto_categoria": producto["categoria"],
                    "paises_venta": ", ".join(producto["pais_venta"]),
                    "tipo": "producto_individual"
                }
            )
            
            all_documents.append(product_doc)
        

        normalized_documents = []
        
        for doc in all_documents:
            normalized_text = self.normalize_text(doc.page_content)
            
            if normalized_text.strip():
                normalized_documents.append({
                    "metadata": doc.metadata,
                    "page_content": normalized_text,
                })
        
        normalized_documents_langchain = [
            Document(page_content=doc["page_content"], metadata=doc["metadata"])
            for doc in normalized_documents
        ]
        
        vector_store = MongoDBAtlasVectorSearch.from_documents(
            documents=normalized_documents_langchain,
            embedding=self.embedding_model,
            collection=self.collection,
            text_key="content",
            index_name="vector_index"
        )
        
        print(f"Productos procesados y almacenados: {len(normalized_documents_langchain)}")

if __name__ == "__main__":
    processor = RagProducts()
    print("Insertando productos de AJE Group...")
    processor.insert()