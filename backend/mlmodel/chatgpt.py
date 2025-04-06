import google.generativeai as genai
import re
import random
# import json

from .gemaudio import evaluate, extract_json_from_text
from .gcs import upload_blob


genai.configure(api_key="AIzaSyCk1ykwF_FyT_JtLr5bFspcX10C1gEoMss")
model = genai.GenerativeModel("gemini-1.5-flash")

def askQuestion(questionSet, history,NOS_count):
    # print(questionSet)
    print(len(history))
    print(NOS_count)
    if len(history) == NOS_count:
        print("All questions have been asked.")
        return None, None, None
    while(True):
        random_index = random.randint(0, len(questionSet) - 1)
        NOS=questionSet[random_index]['NOS']
        question=questionSet[random_index]['question']
        if NOS not in history:
            print("question is not in history")
            correct_answer=questionSet[random_index]['answer']
            # NOS=questionSet[random_index]['NOS']
            return question, correct_answer, NOS 
        
def extract_scores(input_string):

    pattern = r"([\w\s]+): (\d+)/10"
    matches = re.findall(pattern, input_string)
    
    # Convert scores to integers and store in a dictionary
    scores = {label.strip(): int(score) for label, score in matches}
    return scores


def evaluate_answer(question, model_answer, user_answer):
    prompt = (
        "You are a human scoring assistant. Evaluate the user's answer based on the following parameters:\n"
        "- Relevance (out of 10)\n"
        "- Completeness (out of 10)\n"
        "- Accuracy (out of 10)\n"
        "- Depth of Knowledge (out of 10)\n"
        "Also, calculate the total average score out of 10 \n\n"
        f"Model Answer: {model_answer}\n"
        f"User Answer: {user_answer}\n"
    )

    try:
        response = model.generate_content(prompt)
        api_response = response.text
    except Exception as e:
        return {"error": str(e)}, f"Error: {str(e)}"

    scores = {
        "Relevance": 0,
        "Completeness": 0,
        "Accuracy": 0,
        "Depth of Knowledge": 0,
        "Total Average": 0
    }

    try:
        
        for line in api_response.split("\n"):
            for key in scores.keys():
                if key in line:
                    match = re.search(r"(\d+)/10", line)
                    if match:
                        scores[key] = int(match.group(1))

        
        scores["Total Average"] = int(
            (scores["Relevance"] + scores["Completeness"] + scores["Accuracy"] + scores["Depth of Knowledge"]) / 4
        )

       
        summary = (
            f"Scores:\n"
            f"Relevance: {scores['Relevance']}/10\n"
            f"Completeness: {scores['Completeness']}/10\n"
            f"Accuracy: {scores['Accuracy']}/10\n"
            f"Depth of Knowledge : {scores['Depth of Knowledge']}/10\n"
            f"Total Average Score: {scores['Total Average']}/10\n"
        )

        return summary,scores["Total Average"]

    except Exception as parse_error:
        return {"error": f"Error parsing API response: {str(parse_error)}"}, f"Error: {str(parse_error)}"

def feedback_prompt(question, model_answer, user_answer):
  prompt = (
        "You are a human feedback  assistant. give feedback on the user's answer based on the following parameters:\n"
        "- Relevance\n"
        "- Completeness \n"
        "- Accuracy\n"
        "- Depth of Knowledge\n"
        f"Model Answer: {model_answer}\n"
        f"User Answer: {user_answer}\n"
    )
  try:
        response = model.generate_content(prompt)
        api_response = response.text
        return api_response
  except Exception as e:
        return {"error": str(e)}, f"Error: {str(e)}"
  
def finalfeedback(lst):
#   print(lst)
  prompt = (
        f"You are a human feedback  assistant. give feedback's summary on the user's question wise feedback provided in list : {lst}\n. your feedback must be overall not questionwise"

    )
  try:
        response = model.generate_content(prompt)
        api_response = response.text
        return api_response
  except Exception as e:
        return {"error": str(e)}, f"Error: {str(e)}" 
  

def run(uri,p_answer,p_question,domain):
    # summary , score=evaluate_answer(p_question,p_answer,user_input)
    data=""
    max_retries = 5
    retries = 0
    while(type(data) != dict and retries < max_retries):
        evaluate_response = evaluate(uri, p_answer, p_question, domain)
        data = extract_json_from_text(evaluate_response)
        # print(data)
        retries += 1
    if type(data) != dict:
        raise ValueError("Failed to get a valid dictionary response after maximum retries")
    return data


      
def askbot(user_input,uri, questionSet ,p_question,p_answer,history,NOS_count,domain):
    print("at askbot in ml model")

    if user_input.lower() == "start":
        print("user ask for start")
        # Select the first question as an introduction
        interviewer_question,interviewer_answer,NOS=askQuestion(questionSet,history,NOS_count)
        print("question collected")
        return {"question":interviewer_question, "answer":interviewer_answer,'NOS':NOS}
    else:
        print("pre question was "+p_question)
        print("answers was "+p_answer)

        data=run(uri,p_answer,p_question,domain)
        interviewer_question,interviewer_answer,NOS=askQuestion(questionSet,history,NOS_count)
        # print(crew_output)
        print(interviewer_question)
        return  {"question":interviewer_question, "answer":interviewer_answer,"NOS":NOS ,"data":data}