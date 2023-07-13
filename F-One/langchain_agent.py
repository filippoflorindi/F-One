from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain import HuggingFaceHub
from langchain.agents import Tool
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.agents import initialize_agent
import os
from dotenv import load_dotenv

from config import persist_directory
from vector_store import get_vector_store

load_dotenv()

GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
HUGGINGFACEHUB_API_TOKEN = os.getenv('HUGGINGFACEHUB_API_TOKEN')



def llm_model(llm_type):
    if llm_type == "openai":
        ## OpenAI LLM  
        llm = ChatOpenAI(openai_api_key = OPENAI_API_KEY,
                        model_name = "gpt-3.5-turbo",
                        temperature = 0.2,
                        max_tokens = 256,
                        )  
          
    elif llm_type == "hugging face":
        ## Hugging Face LLM 
        llm = HuggingFaceHub(huggingfacehub_api_token = HUGGINGFACEHUB_API_TOKEN,
                             repo_id = "google/flan-t5-xl", 
                             model_kwargs = {"temperature":0, "max_length":64}
                             )
        
    else:
        raise TypeError("This LLM model type is not allowed.")
    
    return llm



def retriever_vector_store(vector_store, llm, k: int):
    retr = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": k})

    retriever = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retr
    )
    return retriever



def tools_agent(retriever):
    tool_F1_Regulations_desc = """Use this tool to answer user questions using the 
    informations about Formula 1 regulations. 
    This tool can also be used for follow up questions from the user.
    This tool has priority over other tools.
    Always use this tool"""


    search = GoogleSearchAPIWrapper(google_cse_id = GOOGLE_CSE_ID,
                                    google_api_key = GOOGLE_API_KEY
                                    )

    tools = [
        Tool(
            func=retriever.run,
            description=tool_F1_Regulations_desc,
            name='F1 Regulations'
        ),
        Tool(
            func=search.run,
            description="A wrapper around Google Search. Useful for when you need to answer questions about current events. Input should be a search query.",
            name = "Search"
        )
    ]

    return tools



def agent(llm, tools):

    memory = ConversationBufferWindowMemory(
        memory_key="chat_history", 
        k=4,
        return_messages=True,
        input_key="input", 
        output_key='output'
    )

    conversational_agent = initialize_agent(
        agent='chat-conversational-react-description', 
        tools=tools, 
        llm=llm,
        verbose=True,
        max_iterations=3,
        early_stopping_method="generate",
        memory = memory,
    )

    #To look the prompt 
    #conversational_agent.agent.llm_chain.prompt

    system_msg = """You are a helpful chatbot that answers the user's questions about Formula 1. Your name is Fone. 
    In addition to responding and providing correct information, you are able to use the emotion expressed by the user to respond sensitively.
    """

    human_msg = """TOOLS
    ------
    Assistant can use tools to look up information that may be helpful in answering the users original question. The tools are:

    {{tools}}


    {format_instructions}

    USER\'S EMOTION
    --------------------
    Here is the user\'s emotion (remember to respond sensitively according to the user\'s emotion):

    {{{{user_emotion}}}}

    USER\'S INPUT
    --------------------
    Here is the user\'s input (remember to respond with a markdown code snippet of a json blob with a single action, and NOTHING else):

    {{{{input}}}} 
    """

    input_var = ['input', 'chat_history', 'user_emotion', 'agent_scratchpad']

    prompt = conversational_agent.agent.create_prompt(
        system_message=system_msg,
        human_message = human_msg,
        input_variables = input_var,
        tools=tools
    )

    conversational_agent.agent.llm_chain.prompt = prompt

    conversational_agent.agent.llm_chain.prompt
    
    return conversational_agent
 



def get_final_answer(text_input, user_emotion):
    vector_store = get_vector_store(persist_directory)

    llm = llm_model(llm_type = 'openai')
    retriever = retriever_vector_store(vector_store, llm, k = 8)
    tools = tools_agent(retriever)
    conversational_agent = agent(llm, tools)
    output = conversational_agent({'input': text_input, 'user_emotion': user_emotion})['output']

    return output




if __name__ == "__main__":

    #text_input = input("")
    text_input = "Who is Charles Leclerc?"
    user_emotion = "None"
    output = get_final_answer(text_input, user_emotion)

    print("\n\n\n\n")
    print(output)