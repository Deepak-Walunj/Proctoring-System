# from google import genai
# import google.genai as genai
import google.generativeai as genai

import json
import re
import os

print(dir(genai))

genai.configure(api_key="AIzaSyCk1ykwF_FyT_JtLr5bFspcX10C1gEoMss")

# Assuming the correct method to get the model is 'load_model'
# model = client.load_model("gemini-1.5-flash")

template={
  "Transcription": "",
  "Speech_analysis": {
    "Grammar_score": 0/10,
    "Fluency_score": 0/10,
    "Vocabulary_score": 0/10,
    "Pauses": 0,
    "Overall_confidence": 0/10
  },
  "human_evaluation": {
    "Relevance": 0/10,
    "Completeness": 0/10,
    "Accuracy": 0/10,
    "Depth of Knowledge": 0/10,
    "Total Average Score": 0/10
  },
  "feedback": ""
}
model_answer="i am friendly and i am a good person. i speak politly with others. "

myfile = 'C:/Development/Web-Dev/Project-1/Semester_project/backend/mlmodel/audio_gtJyDGw.wav'



def evaluate(file, model_answer):
    
    prompt = f"""
    Strictly give me the complete transcription of this audio file. Compare the transcription with the model answer="{model_answer}" and give the humanized scores out of 10 (using decimal values like 7.5, not 7/10). Also, give the speech analysis of the audio file.  Return ONLY a JSON object that strictly adheres to this template:

    ```json
    {json.dumps(template)}
    Do not include any other text or explanations in your response.  The entire output should be a valid JSON string that can be directly parsed.
    """
    myfile = genai.upload_file(file)
    # response = genai
    response = genai.embed_content(
        model="gemini-1.5-flash",
     file=myfile,
    prompt=prompt
    )
    return response.text


# response = client.models.generate_content(
#     model="gemini-1.5-flash",
#   contents=[
#       prompt
#     ,
#     myfile,
#   ]
# )

# print(response.text)

res=evaluate("C:/Development/Web-Dev/Project-1/Semester_project/backend/mlmodel/audio_gtJyDGw.wav", model_answer)


def extract_json_from_text(text):
    try:
        # Regular expression to find a JSON object in text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)  # Extract the JSON string
            return json.loads(json_str)  # Convert to Python dictionary
        else:
            print("No JSON object found in the text.")
            return None
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return None
    
print(extract_json_from_text(res))