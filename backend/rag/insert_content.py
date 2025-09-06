import re
from unidecode import unidecode
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from connection import MongoDB, Bedrock

class RagDocument:
    def __init__(self):
        self.RUTA_DOCUMENTO = "./docs/content.pdf"
        self.bedrock = Bedrock()
        self.mongo = MongoDB()
        self.embedding_model = self.bedrock.embedding_model()
        self.collection = self.mongo.mongo_client()
        self.footer_patterns = [
            r'^\d+\s*\|\s*p\s*á\s*g\s*i\s*n\s*a\s*$',
            r'^\d+\s*\|\s*página\s*$'
        ]

    def extract_text_from_pdf(self, pdf_path):
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        return documents

    def remove_accents(self, text):
        return unidecode(text)

    def clean_headers_footers(self, text):
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line_clean = line.strip().lower()
            
            if not line_clean:
                continue
                
            is_header_footer = False
            for pattern in self.footer_patterns:
                if re.match(pattern, line_clean):
                    is_header_footer = True
                    break
            
            if len(line_clean) <= 3 and line_clean.isdigit():
                is_header_footer = True
            
            if re.match(r'^\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}$', line_clean):
                is_header_footer = True
                
            if not is_header_footer:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def normalize_text(self, text):
        text = self.clean_headers_footers(text)
        text = text.lower()
        text = text.replace("\n", " ")
        text = re.sub(r"\s+", " ", text).strip()
        text = self.remove_accents(text)
        return text

    def insert(self):
        raw_text = self.extract_text_from_pdf(self.RUTA_DOCUMENTO)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1040, 
            chunk_overlap=100
        )
        documents = text_splitter.split_documents(documents=raw_text)

        normalized_documents = []

        for doc in documents:
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
        
        print(f"Documentos procesados y almacenados: {len(normalized_documents_langchain)}")


if __name__ == "__main__":
    processor = RagDocument()
    print(f"Insertando documentos ...")
    processor.insert()