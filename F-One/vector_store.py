import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from IPython.display import display, Markdown
from dotenv import load_dotenv


from config import path_directory, persist_directory
from process_pdf import get_final_docs

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')



def embeddings_init(emb_type):

    if emb_type == "openai":
        ## OpenAI Embedding
        embeddings = OpenAIEmbeddings(model = 'text-embedding-ada-002',
                                      openai_api_key = OPENAI_API_KEY
                                     )
        
    elif emb_type == "hugging face":
        ## Hugging Face Embedding
        model_name = "sentence-transformers/all-mpnet-base-v2"
        embeddings = HuggingFaceEmbeddings(model_name=model_name)

    else:
        raise TypeError("This Embeddings model type is not allowed.")
    
    return embeddings



def create_vector_store(split_docs, embeddings, persist_directory):
    #Creating Vector Store
    vector_store = FAISS.from_documents(split_docs, 
                                    embedding = embeddings
                                    )
    
    vector_store.save_local(persist_directory)

    return vector_store




def load_vector_store(embeddings, persist_directory):
    #Load vector store from local directory
    if os.path.exists(persist_directory):
        vector_store = FAISS.load_local(
                                        persist_directory,
                                        embeddings
                                        )
    else:
        raise TypeError("Missing files. Create Vector Store and upload files to {persist_directory} directory first.")
    
    return vector_store




def verify_vector_store_content(vector_store):
    #Verify Content of Vector Store with a simple query
    search_result = vector_store.similarity_search_with_score("what are the sporting regulations on the extra formation lap?", 
                                                            k= 8, 
                                                            #filter = {"Chapter": {"$eq": "45) EXTRA FORMATION LAP\n"}}
                                                            ) 
    search_result

    line_separator = "\n"      
    return display(Markdown(f"""## Search results:{line_separator}
                            {line_separator.join([
                            f'''
                            {line_separator}{line_separator}Source:{line_separator}{r[0].metadata['source']}
                            {line_separator}Page:{line_separator}{r[0].metadata['Page Number']}
                            {line_separator}Chapter:{line_separator}{r[0].metadata['Chapter']}
                            {line_separator}Paragraph:{line_separator}{r[0].metadata['Paragraph']}
                            {line_separator}Sub Paragraph:{line_separator}{r[0].metadata['Sub Paragraph']}
                            {line_separator}Score:{line_separator}{r[1]}
                            {line_separator}Content:{line_separator}{r[0].page_content}
                            '''
                            for r in search_result
                            ])}
                            """))


def get_vector_store(persist_directory):
    embeddings = embeddings_init(emb_type = 'openai')

    if len(os.listdir(persist_directory)) == 0:
        _ ,split_docs = get_final_docs(path_directory)
        vector_store = create_vector_store(split_docs, embeddings, persist_directory)
    else:
        vector_store = load_vector_store(embeddings, persist_directory)
    
    return vector_store




if __name__ == "__main__":

    vector_store = get_vector_store(persist_directory)

    verify_vector_store_content(vector_store)