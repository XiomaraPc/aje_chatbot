from langchain.agents import Tool
from utils.template_util import TemplateUtil
from config.logger_config import get_logger
from repositories.vector_repository import MongoDBRepository, Bedrock
from connections.llm import LLMManager
import base64
import json
import os 
from dotenv import load_dotenv

load_dotenv()
log = get_logger()


class ToolsService:
    def __init__(self):
        self.template = TemplateUtil()
        self.mongo = MongoDBRepository()
        self.llm_manager = LLMManager()  
        self.bedrock = Bedrock()
        self.llm = self.llm_manager.get_llm()
        self.model_ = os.getenv('EMBEDDING_MODEL_IMAGE')
        self.vector_search = self.mongo.vector_store_inference()
        self.bedrock_client = self.bedrock.client()
        self.tools = [
                Tool(
                    name="ConsultarEstrategia",
                    func=self.tool_consultar_estrategia,
                    description="Consulta información sobre estrategia de internacionalización de AJE Group",
                    return_direct=True
                ),
                Tool(
                    name="ConsultarProducto",
                    func=self.tool_consultar_producto,
                    description="Consulta información sobre productos de AJE",
                    return_direct=True
                ),
                Tool(
                    name="BuscarProductoImagen",
                    func=self.tool_buscar_producto_imagen,
                    description="Buscar que producto es en una imagen guardada",
                    return_direct=True
                )
            ]
        
    def get_tools (self):
        return self.tools
    
    def tool_consultar_estrategia(self, query: str) -> str:
        try:
            
            documentos = self.vector_search.similarity_search(query, k=3)
            
            if not documentos:
                return json.dumps("No encontré información para la consulta.")
            
            contexto = "\n\n".join([doc.page_content for doc in documentos])
            
            prompt = self.template.prompt_consultar_estrategia()
            formatted_prompt = prompt.format(
                query=query,
                contexto=contexto
            )
            
            response = self.llm.invoke(formatted_prompt)
            return response.content
            
        except Exception as e:
            return json.dumps({"respuesta": f"Error consultando estrategia: {str(e)}"})

    def tool_consultar_producto(self, query: str) -> str:
        try:
            log.info(query)
            
            documentos = self.vector_search.similarity_search(query=query, k=2)
            
            results = "\n".join([doc.page_content for doc in documentos])
            
            if not results:
                return json.dumps({"respuesta": "No encontré información sobre el producto."})

            prompt = self.template.prompt_productos()
            formatted_prompt = prompt.format(
                results=results,
                query=query
            )
            
            response = self.llm.invoke(formatted_prompt)
            return response.content
            
        except Exception as e:
            return json.dumps({"respuesta": f"Error consultando producto: {str(e)}"})

    def image_to_base64(self, image_path: str):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
        
    def tool_buscar_producto_imagen(self, type) -> str:
        try:
            image_path = "./uploads/image.png"
            image_base64 = self.image_to_base64(image_path)
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_,
                body=json.dumps({
                    "inputImage": image_base64,
                    "embeddingConfig": {"outputEmbeddingLength": 1024}
                }),
                contentType="application/json"
            )
            
            image_embedding = json.loads(response['body'].read())['embedding']
            
            collection = self.mongo.get_collection_()  
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index_images",
                        "path": "embedding", 
                        "queryVector": image_embedding,
                        "numCandidates": 5,
                        "limit": 1
                    }
                },
                {
                    "$project": {
                        "product_name": 1,
                        "score": {"$meta": "vectorSearchScore"}
                    }
                }
            ]
            
            results = list(collection.aggregate(pipeline))
            if results:
                product_name = results[0]['product_name']
                log.info(f"La imagen es del siguiente producto :  {product_name}")            

                return self.tool_consultar_producto(product_name)
            else:
                return "No se pudo identificar el producto en la imagen"
                
        except Exception as e:
            return f"Error buscando imagen: {str(e)}"