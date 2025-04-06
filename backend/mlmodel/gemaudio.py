from google import genai
from google.genai import types
import base64
from google.auth import load_credentials_from_file
import os
from vertexai.generative_models import GenerativeModel,Part
import json
import re


# 1. Set the environment variable (important for some setup)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the relative path
credentials_path = os.path.join(current_dir, "gen-lang-client-0166846330-97747717adf2.json")

# Set the environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# 2. Load credentials directly (make sure to adjust this according to your function's needs)
credentials, project_id = load_credentials_from_file(credentials_path)
print(credentials)

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
template ="""
{
  "transcribed text": [Insert the transcribed text of the Candidate's Audio File here],
  "language of candidates response": [Evaluator to fill in this field],

  "content evaluation": {
    "completeness": {score,feedback},
    "accuracy":{score,feedback},
    "relevance": {score,feedback},
    "depth of knowledge": {score,feedback},
    "content score": {score,feedback}
  },
  "speech analysis": {
    "fluency": {score,feedback},
    "clarity": {score,feedback},
    "coherence": {score,feedback},
    "grammar": {score,feedback},
    "vocabulary": {score,feedback},
    "pauses": {score,feedback},
    "stuttering/stmmering": {score,feedback},
    "filler words": {score,feedback},
    "speech score": {score,feedback}
    },
    "overall score": score,
    "overall feedback": [Give a summary on the evaluation based on content evaluation and speech analysis]
}
"""

def evaluate(gcs_uri, model_answer,question,domain):
    prompt = f"""
Evaluate a Student's Audio Answer with Speech Analysis and Penalties

Instructions:
Transcribe the provided audio file containing the candidate's response to the given question.
Identify and record the language of candidate's response.
If the audio file content is blank and the transcription response is blank/empty then set Transcription Word Count = 0 and set Language of Candidates Response as No Response.
Count the words in the provided model answer. (You can use a word processor's word count feature or any online word counter.) Record this word count below.
Evaluate the transcribed response and the audio itself based on the provided model answer and the rubric below. Assign scores (0-10) for each parameter. Apply penalty adjustments as described. Provide constructive feedback justifying your scores and penalty applications.
Calculate a average score for both content and speech quality.

Question: "{question}"

Domain: "{domain}"

Model Answer: "{model_answer}"

Candidate's Audio File: "{gcs_uri}"

Rubric:

Rubric: Content Evaluation

Relevance (0-10): How well does the transcribed response address the question and align with the key points of the model answer? 10 = perfect alignment; 0 = completely irrelevant.

Completeness (0-10): How thoroughly does the transcribed response cover the aspects addressed in the model answer? 10 = all key aspects covered in detail; 0 = no key aspects covered. (Subject to Word Count Penalty)

Accuracy (0-10): How factually correct is the information presented in the transcribed response compared to the model answer? 10 = complete factual accuracy; 0 = significant inaccuracies or misinformation. (Subject to Question Repetition Penalty)

Depth of Knowledge (0-10): Does the response demonstrate a detailed understanding of the domain, going beyond superficial knowledge? 10 = deep understanding; 0 = very superficial understanding. (Subject to Word Count Penalty)

If transcription word count is less than 3 then set Relevance = 0, Completeness = 0, Accuracy = 0, Depth of Knowledge = 0

Rubric: Speech Analysis

Fluency (0-10): Smoothness and naturalness of speech; absence of hesitations and interruptions. 10 = effortless and natural flow; 0 = extremely halting and disjointed.

Clarity (0-10): How easily understandable the speech is; articulation and pronunciation. 10 = perfectly clear; 0 = very difficult to understand.

Coherence (0-10): Logical organization and flow of ideas within the response. 10 = perfectly organized and logical; 0 = completely disorganized and illogical.

Grammar (0-10): Grammatical correctness of the spoken language. 10 = grammatically perfect; 0 = riddled with grammatical errors.

Vocabulary (0-10): Appropriateness and richness of vocabulary used. 10 = sophisticated and precise language; 0 = limited and inappropriate vocabulary.

Pauses (0-10): Effective use of pauses for emphasis and clarity (not excessive). 10 = pauses used effectively; 0 = excessive or disruptive pauses.

Stammering/Stuttering (0-10): Frequency and severity of stammering or stuttering. 10 = no stammering; 0 = frequent and severe stammering.

Use of Filler Words (0-10): Frequency of using filler words ("um," "uh," "like," "hmm","ah", etc.). 10 = no filler words; 0 = excessive use of filler words.

If transcription word count is less than 3 then set Fluency = 0, Clarity = 0, Coherence = 0, Grammar = 0, Vocabulary = 0, Pauses = 0, Stammering/Stuttering = 0, Filler Words = 0

Penalty Adjustments:

Word Count Penalty: If the transcribed response contains less than 50% of the word count of the model answer, deduct at least 1 points from all parameters "Relevance", "Completeness" , "Accuracy" and "Depth of Knowledge"

Question Repetition Penalty: If the transcription only repeats the question, set Completeness = 0, Accuracy = 0, Relevance = 1 (maximum), and Depth of Knowledge = 0.


Transcribed Text: [Insert the transcribed text of the Candidate's Audio File here]

Language of Candidates Response: [Evaluator to fill in this field]

Scoring and Feedback:

(Content Section) (Penalties applied here)

Parameter Score (0-10)	Feedback
Relevance
Completeness
Accuracy
Depth of Knowledge

(Speech Analysis Section) (No penalties apply here)

Parameter	Score (0-10)	Feedback
Fluency
Clarity
Coherence
Grammar
Vocabulary
Pauses
Stammering/Stuttering
Filler Words

Average Scores:

Content Score: (Relevance + Completeness + Accuracy + Depth of Knowledge)/4 = [Calculate and insert score]

Speech Score: (Fluency + Clarity + Coherence + Grammar + Vocabulary + Pauses + Stammering/Stuttering + Filler Words) / 8 = [Calculate and insert score]

Overall Score: (Content Score + Speech Score) / 2 = [Calculate and insert score]

Overall Feedback : Give a summary on the evaluation based on content evaluation and speech analysis

Generate the output in the following format: "{template}"

"""
    try:
        # Correct way to provide GCS audio to Gemini
        # print("getting audio")
        audio_part = Part.from_uri(gcs_uri, mime_type="audio/wav")  # Correct MIME type!
        # print((model.generate_content))
        response = model.generate_content([prompt, audio_part])  # Provide both prompt and audio

       # print(response.text)
        return response.text

    except Exception as e:
        print(f"An error occurred: {e}")





def extract_json_from_text(text):
    """Extracts and returns a JSON object from a given string."""
    try:
        # Find JSON object using regex
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)  # Convert to dictionary
        else:
            return None  # No JSON found
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return None


# res=evaluate(gcs_uri=gcs_uri,model_answer=model_answer,question=question,domain=domain)
# print(extract_json_from_text(res))