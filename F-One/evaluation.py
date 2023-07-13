# Generated examples
from langchain.evaluation.qa import QAGenerateChain
from langchain.evaluation.qa import QAEvalChain
from inspiredco.critique import Critique
import os
from dotenv import load_dotenv

from config import path_directory 
from config import persist_directory
from process_pdf import create_final_docs, split_final_docs
from vector_store import get_vector_store
from langchain_agent import llm_model, retriever_vector_store

load_dotenv()

INSPIREDCO_API_KEY = os.getenv('INSPIREDCO_API_KEY')



def examples_auto_generation(split_docs, llm, min_num_docs: int, max_num_docs: int):
    example_gen_chain = QAGenerateChain.from_llm(llm)
    examples = example_gen_chain.apply_and_parse([{"doc": t} for t in split_docs[min_num_docs:max_num_docs]])
    return examples



def examples_manual():
    examples = [
        {
            "query": """How is the "Capital Expenditure Amount" defined?""",
            "answer": """The "Capital Expenditure Amount" is defined as follows:
(a) For the Full Year Reporting Period ending on 31 December 2022, it is the aggregate amount of Capital Expenditure for that period and the preceding Full Year Reporting Period, minus any Adjustment made pursuant to Article 4.1(e) for the preceding Full Year Reporting Period.
(b) For the Full Year Reporting Period ending on 31 December 2023, it is the aggregate amount of Capital Expenditure for that period and the preceding two Full Year Reporting Periods, minus the cumulative amount of Adjustments made pursuant to Article 4.1(e) for the preceding two Full Year Reporting Periods.
(c) For the Full Year Reporting Period ending on 31 December 2024 and each subsequent Full Year Reporting Period, it is the aggregate amount of Capital Expenditure for the relevant period and the three preceding Full Year Reporting Periods, minus the cumulative amount of Adjustments made pursuant to Article 4.1(e) for the preceding three Full Year Reporting Periods.

"""
        },
        {
            "query": """What is meant by the term "Engineering Trailer"?""",
            "answer": """The term "Engineering Trailer" refers to a branded temporary standalone structure that is brought into the paddock by an F1 Team. It includes any irremovable fixtures, fittings, and equipment integrated into the structure. The purpose of the Engineering Trailer is to provide a working environment for engineering activities during a Competition or Testing of Current Cars. It's important to note that the definition excludes any structures, fixtures, fittings, or equipment that are constructed or installed into permanent or existing paddock buildings, such as the pit garages.


"""
        }
    ]    
    return examples



def examples_combination(path_directory, llm, min_num_docs: int, max_num_docs: int):
    examples_1 = examples_manual()

    documents = create_final_docs(path_directory)
    split_docs = split_final_docs(documents) 
    examples_2 = examples_auto_generation(split_docs, llm, min_num_docs, max_num_docs)
    # Combine examples
    examples = examples_1 + examples_2
    return examples


def generate_predictions(retriever, examples):
    predictions = retriever.apply(examples)
    return predictions



def simple_qa_evaluation(llm, examples, predictions):
    eval_chain = QAEvalChain.from_llm(llm)
    graded_outputs = eval_chain.evaluate(examples, predictions)
    for i, eg in enumerate(examples):
        print(f"Example {i}:")
        print("Question: " + predictions[i]['query'])
        print("Real Answer: " + predictions[i]['answer'])
        print("Predicted Answer: " + predictions[i]['result'])
        print("Predicted Grade: " + graded_outputs[i]['text'])
        print()
    


def qa_evaluation_with_metrics(examples, predictions):
    client = Critique(api_key = INSPIREDCO_API_KEY )
    metrics = {
        "bleu": {
            "metric": "bleu",
            "config": {"max_ngram_order": 2, "smooth_method": "add_k"},
        },
        "chrf": {
            "metric": "chrf",
            "config": {},
        },
        "bert_score": {
            "metric": "bert_score",
            "config": {"model": "bert-base-uncased"},
        },
        "uni_eval": {
            "metric": "uni_eval",
            "config": {"task": "summarization", "evaluation_aspect": "relevance"},
        },
    }
    critique_data = [
        {"target": pred['result'], "references": [pred['answer']]} for pred in predictions
    ]
    #print(critique_data)
    eval_results = {
        k: client.evaluate(dataset=critique_data, metric=v["metric"], config=v["config"]) 
        for k, v in metrics.items()
    }

    for i, eg in enumerate(examples):
        score_string = ", ".join([f"{k}={v['examples'][i]['value']:.4f}" for k, v in eval_results.items()])
        print(f"Example {i}:")
        print("Question: " + predictions[i]['query'])
        print("Real Answer: " + predictions[i]['answer'])
        print("Predicted Answer: " + predictions[i]['result'])
        print("Predicted Scores: " + score_string)
        print()



def final_evaluation(examples_type, eval_type):
    vector_store = get_vector_store(persist_directory)
    llm = llm_model(llm_type = 'openai')
    retriever = retriever_vector_store(vector_store, llm, k = 8)

    if examples_type == "manual":
        examples = examples_manual()
    elif examples_type == "auto gen":
        documents = create_final_docs(path_directory)
        split_docs = split_final_docs(documents)    
        examples = examples_auto_generation(split_docs, llm, min_num_docs = 1000, max_num_docs = 1002)
    elif examples_type == "combo":
        examples_combination(path_directory, llm, min_num_docs = 1000, max_num_docs = 1002)
    else:
        raise TypeError("This Examples type is not allowed.")
    
    predictions = generate_predictions(retriever, examples)

    if eval_type == "simple":
        simple_qa_evaluation(llm, examples, predictions)
    elif eval_type == "with metrics":
        qa_evaluation_with_metrics(examples, predictions)
    else:
        raise TypeError("This Evaluation type is not allowed.")
    



if __name__ == "__main__":

    final_evaluation(examples_type = "manual", eval_type = "with metrics")