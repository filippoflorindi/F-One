from flask import Flask
from flask import Response, request
import json
import numpy as np
import os
import sys
from dotenv import load_dotenv


from config import persist_directory
from vector_store import get_vector_store
from langchain_agent import agent, llm_model, retriever_vector_store, tools_agent
from emotion_detection import emotion_classifier


load_dotenv()

GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
HUGGINGFACEHUB_API_TOKEN = os.getenv('HUGGINGFACEHUB_API_TOKEN')
INSPIREDCO_API_KEY = os.getenv('INSPIREDCO_API_KEY')





# Initialize the flask app
app=Flask(__name__)


# Default route
#@app.route('/')
#def hello():
#    return ''

session_names = []
# Create a route for Webhook
# Getting and Sending response to Dialogflow
@app.route('/webhook', methods=['POST'])

def webhook():

    req = request.get_json(silent=True, force=True) 
    res = processRequest(req)
    r = answer_webhook(res)

    return r  #Final Response sent to DialogFlow



# Processes the incoming request 
def processRequest(req):    
    try:
        tag = req['fulfillmentInfo']['tag']
        query_text = req['text']
        print("\n")
        print(query_text)
        session_info = req['sessionInfo']['session']
        session_names.append(session_info)

        global conversational_agent

        if len(session_names) > 1:
            if session_names[-1] != session_names[-2]:
                conversational_agent = agent_initialization()
        else:
            conversational_agent = agent_initialization()

        if tag == 'f1':
            user_emotion = get_emotion_label(query_text)
            print("\n")
            print(user_emotion)
            #user_emotion = "none"
            response = get_final_answer(query_text, user_emotion, conversational_agent)

            return response
    
    except Exception as e:
        print("\n")
        print('The Error is: ',e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('Error Info: ',exc_type, fname, exc_tb.tb_lineno)
        return """I'm sorry, there's an error answering to this message."""



def get_emotion_label(query_text):
    emotion = emotion_classifier(query_text)
    return emotion['label']


def agent_initialization():
    vector_store = get_vector_store(persist_directory)

    llm = llm_model(llm_type = 'openai')
    retriever = retriever_vector_store(vector_store, llm, k = 8)
    tools = tools_agent(retriever)
    conversational_agent = agent(llm, tools)
    return conversational_agent


def get_final_answer(query_text, user_emotion, conversational_agent):
    
    output = conversational_agent({'input': query_text, 'user_emotion': user_emotion})["output"]

    return output


def answer_webhook(msg):
    message= {"fulfillment_response": {
      
        "messages": [
        {
          "text": {
            "text": [msg]
          }
        }
      ]
    }
    }
    return Response(json.dumps(message), 
                    status = 200, 
                    mimetype='application/json')



# Run the application
if __name__ == "__main__":
    app.run()

