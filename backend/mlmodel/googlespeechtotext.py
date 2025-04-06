from google import genai
from google.genai import types
import base64
from google.auth import load_credentials_from_file
import os
from vertexai.generative_models import GenerativeModel,Part
import json
import re


# 1. Set the environment variable (important for some setup)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Development/Web-Dev/Project-1/Semester_project/backend/mlmodel/gen-lang-client-0166846330-97747717adf2.json"

# 2. Load credentials directly
credentials, project_id = load_credentials_from_file(
    "C:/Development/Web-Dev/Project-1/Semester_project/backend/mlmodel/gen-lang-client-0166846330-97747717adf2.json"
)

client = genai.Client(
      vertexai=True,
      project="gen-lang-client-0166846330",
      location="us-central1",
      credentials=credentials
  )

# print(dir(client))
# myfile = client.files.upload("gs://eduviva/audio_gtJyDGw.wav")

model = GenerativeModel("gemini-1.5-flash")
# gcs_uri = "gs://eduviva/audio_gtJyDGw.wav"
gcs_uri="gs://eduviva/converted_mono_audio.wav"

domain="armed-security-guard"
question= "how to behavein public place"
model_answer="you must say good morning sir. happy birthday. have a nice day . salute them"
template={
  "Transcription": "",
  "Speech_analysis": {
    "Grammar score": 0/10,
    "Fluency score": 0/10,
    "Vocabulary score": 0/10,
    "Pauses": 0,
    "Overall confidence": 0/10
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

def evaluate(gcs_uri, model_answer,question,domain):
    prompt = f"""
            You are an advanced human scoring assistant and an expert in the field of {domain}.
            Your task is to analyze the given audio file for the question: "{question}" and compare 
            its extracted transcription with the provided model answer: "{model_answer}".  

            ### **Instructions:**  

            1. **Transcribe the Audio**  
            - Extract the **complete and accurate transcription** of the provided audio file.  

            2. **Score the Response** (on a scale of 0 to 10, using decimal values like 7.5, not 7/10)  
            - **Relevance:** How well does the transcribed response align with the model answer?  
            - **Completeness:** How complete is the transcribed response compared to the model answer? If the response is very short or incomplete,
            **this score should be significantly lower**.  
            - **Accuracy:** How correctly does the transcribed response match the model answer?  
            - **Depth of Knowledge:** Does the response demonstrate detailed understanding beyond surface-level knowledge?  

            3. **Penalty Adjustments**  
            - If the transcription is **less than 50% of the model answer's word count**, deduct **at least 3 points** from **Completeness** and
            **Depth of Knowledge**.  
            - If the transcription **only repeats the question**, set **Completeness = 0**, **Relevance = 1 max**, and **Depth of Knowledge = 0**.  

            4. **Speech Analysis**  
            - Analyze the speech in terms of **clarity, fluency, pronunciation, pauses, and confidence**.
            **However, speech quality should NOT inflate content scores.**  

            ### **Output Format:**  
            - Return **ONLY a JSON object** strictly following this template:  

            ```json
            {json.dumps(template)}
            DO NOT include any additional text, explanations, or formatting outside of the JSON object.
            Ensure the response is a fully valid JSON string that can be directly parsed.
    """

    try:
        # Correct way to provide GCS audio to Gemini
        print("getting audio")
        audio_part = Part.from_uri(gcs_uri, mime_type="audio/wav")  # Correct MIME type!

        response = model.generate_content(
            [prompt, audio_part]  # Provide both prompt and audio
        )

        print(response.text)
        return response.text

    except Exception as e:
        print(f"An error occurred: {e}")


def extract_json_from_text(text):
  #replace _ from by ' ' in text
    # text=text.replace('_',' ')
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


res=evaluate(gcs_uri=gcs_uri,model_answer=model_answer,question=question,domain=domain)
print(extract_json_from_text(res))