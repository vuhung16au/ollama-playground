import ollama
from langchain_ollama import OllamaEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
import time
from logger import app_logger

class ImageStore:

    embeddings = OllamaEmbeddings(model="llama3.2")
    vector_store = InMemoryVectorStore(embedding=embeddings)

    document_ids_to_images = {}
    document_ids_to_documents = {}

    images_directory = 'images/'

    @classmethod
    @app_logger.profile_function("image_upload")
    def upload_image(cls, file):
        app_logger.log_info(f"Starting image upload for file: {file.name}")
        
        start_time = time.time()
        try:
            with open(cls.images_directory + file.name, "wb") as f:
                f.write(file.getbuffer())

            description = cls._describe_image(cls.images_directory + file.name)
            document = Document(page_content=description)
            document_id = cls.vector_store.add_documents([document])[0]
            cls.document_ids_to_images[document_id] = file.name
            cls.document_ids_to_documents[document_id] = document

            execution_time = time.time() - start_time
            app_logger.log_upload_operation(file.name, execution_time, success=True)
            app_logger.log_info(f"Successfully uploaded image: {file.name} with document ID: {document_id}")
            
            return document_id
            
        except Exception as e:
            execution_time = time.time() - start_time
            app_logger.log_upload_operation(file.name, execution_time, success=False)
            app_logger.log_error(f"Failed to upload image: {file.name}", e)
            raise e


    @classmethod
    @app_logger.profile_function("image_description_generation")
    def _describe_image(cls, image_path):
        app_logger.log_info(f"Generating description for image: {image_path}")
        
        try:
            res = ollama.chat(
                model="llava:34b",
                messages=[
                    {
                        'role': 'user',
                        'content': 'Tell me what do you see in this picture in only one sentence. Be concise.',
                        'images': [image_path]
                    }
                ],
                options={'temperature': 0}
            )

            description = res['message']['content']
            app_logger.log_info(f"Generated description for {image_path}: {description}")
            return description
            
        except Exception as e:
            app_logger.log_error(f"Failed to generate description for image: {image_path}", e)
            raise e

    @classmethod
    @app_logger.profile_function("image_search_by_query")
    def retrieve_docs_by_query(cls, query, k=1):
        app_logger.log_info(f"Starting image search for query: '{query}' with k={k}")
        
        start_time = time.time()
        try:
            results = cls.vector_store.similarity_search_with_score(query, k=k)
            # Add similarity scores to documents
            docs_with_scores = []
            for doc, score in results:
                doc.metadata = doc.metadata or {}
                doc.metadata['score'] = score
                docs_with_scores.append(doc)
            
            execution_time = time.time() - start_time
            app_logger.log_search_operation(query, k, execution_time, len(docs_with_scores))
            app_logger.log_info(f"Search completed. Found {len(docs_with_scores)} results for query: '{query}'")
            
            return docs_with_scores
            
        except Exception as e:
            # Fallback to regular search if similarity_search_with_score is not available
            app_logger.log_warning(f"similarity_search_with_score failed, falling back to regular search: {str(e)}")
            try:
                results = cls.vector_store.similarity_search(query, k=k)
                execution_time = time.time() - start_time
                app_logger.log_search_operation(query, k, execution_time, len(results))
                app_logger.log_info(f"Fallback search completed. Found {len(results)} results for query: '{query}'")
                return results
            except Exception as fallback_error:
                execution_time = time.time() - start_time
                app_logger.log_error(f"Both search methods failed for query: '{query}'", fallback_error)
                raise fallback_error

    @classmethod
    @app_logger.profile_function("reverse_image_search")
    def retrieve_docs_by_image(cls, image, k=1):
        app_logger.log_info(f"Starting reverse image search for image: {image.name}")
        
        start_time = time.time()
        try:
            with open(cls.images_directory + image.name, "wb") as f:
                f.write(image.getbuffer())

            description = cls._describe_image(cls.images_directory + image.name)
            results = cls.retrieve_docs_by_query(description, k=k)
            
            execution_time = time.time() - start_time
            app_logger.log_reverse_search_operation(image.name, execution_time, len(results))
            
            return results
            
        except Exception as e:
            execution_time = time.time() - start_time
            app_logger.log_error(f"Reverse image search failed for image: {image.name}", e)
            raise e

    @classmethod
    def get_by_id(cls, doc_id):
        return cls.document_ids_to_documents[doc_id]

    @classmethod
    def get_image_path_by_id(cls, doc_id):
       return cls.images_directory + cls.document_ids_to_images[doc_id]

