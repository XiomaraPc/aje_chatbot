from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor
from langchain.agents import create_tool_calling_agent
from repositories.vector_repository import MongoDBRepository, Bedrock
from connections.llm import LLMManager
from services.tools_service import ToolsService
from services.memory_service import MemoryService 
from utils.template_util import TemplateUtil
from dotenv import load_dotenv
load_dotenv()

class AJEChatbot:
    def __init__(self, user_id, chat_id):
        self.user_id = user_id
        self.chat_id = chat_id
        self.mongo = MongoDBRepository()
        self.bedrock = Bedrock()
        self.llm_manager = LLMManager()
        self.tools_service = ToolsService()
        self.template = TemplateUtil()
        self.memory_service = MemoryService()
        
        self.tools = self.tools_service.get_tools()
        self.llm = self.llm_manager.get_llm()
        self.embedding_model = self.bedrock.embedding_model()
        self.collection = self.mongo.get_collection()
        
        self.vector_search = self.mongo.vector_store_inference()
        self.agent = None
        self.initialize_components()

    def initialize_components(self):
        try:
            prompt = PromptTemplate(
                input_variables=["input"],
                template= self.template.prompt_general()
            )
            
            agent = create_tool_calling_agent(self.llm, self.tools, prompt)
            
            self.agent = AgentExecutor(
                agent=agent,
                tools= self.tools,
                verbose=True,
                return_direct=True
            )

        except Exception as e:
            raise Exception(f"Error inicializando agente: {str(e)}")
    
    def process_message(self, message: str):
        try:
            history = self.memory_service.get_chat_messages(self.user_id, self.chat_id)
            
            response = self.agent.invoke({
                "input": message,
                "chat_history": history
            })
            print("response", response)
            try:
                response_text = response['output'][0]['text']
            except (TypeError, IndexError, KeyError):
                response_text = response['output']
            # response_text = response_text.replace("\n\n", "\n")
            return response_text

        except Exception as e:
            return {"respuesta": f"Error procesando mensaje: {str(e)}"}