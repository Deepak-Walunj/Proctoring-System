import google.generativeai as genai
import re

genai.configure(api_key="AIzaSyCk1ykwF_FyT_JtLr5bFspcX10C1gEoMss")
model = genai.GenerativeModel("gemini-1.5-flash")

def analyze_grammar(sentence):
  """
  Analyzes the grammatical correctness of the given sentence using Gemini.

  Args:
    sentence: The sentence to be analyzed.

  Returns:
    A score out of 10 for grammatical correctness.
  """
  prompt = f"Analyze the grammatical correctness of the following sentence: '{sentence}'. " \
           f"Give a score out of 10 for grammatical correctness."
  response = model.generate_content(prompt) 
  try:
    score_str = re.search(r"Score: (\d+)", response.text).group(1)
    return int(score_str)
  except AttributeError:
    print(f"Could not extract score from response: {response.text}")
    return None

# def analyze_vocabulary(sentence):
#   """
#   Analyzes the vocabulary used in the given sentence using Gemini.

#   Args:
#     sentence: The sentence to be analyzed.

#   Returns:
#     A score out of 10 for vocabulary richness and appropriateness.
#   """
#   prompt = f"Evaluate the vocabulary used in the sentence: '{sentence}'. " \
#            f"Give only out of 10 for vocabulary richness and appropriateness."
#   response = model.generate_content(prompt) 
#   try:
#     score_str = re.search(r"Score: (\d+)", response.text).group(1)
#     return int(score_str)
#   except AttributeError:
#     print(f"Could not extract score from response: {response.text}")
#     return None

# def analyze_pronunciation(sentence):
#   """
#   Analyzes the sentence for potential pronunciation challenges using Gemini.

#   Args:
#     sentence: The sentence to be analyzed.

#   Returns:
#     A score out of 10 for ease of pronunciation.
#   """
#   prompt = f"Evaluate the ease of pronunciation for the following sentence: '{sentence}'. " \
#            f"Give a score out of 10, with 10 being the easiest to pronounce."
#   response = model.generate_content(prompt) 
#   try:
#     score_str = re.search(r"Score: (\d+)", response.text).group(1)
#     return int(score_str)
#   except AttributeError:
#     print(f"Could not extract score from response: {response.text}")
#     return None

def analyze_fluency(sentence):
  """
  Analyzes the fluency of the given sentence using Gemini.

  Args:
    sentence: The sentence to be analyzed.

  Returns:
    A score out of 10 for sentence fluency and readability.
  """
  prompt = f"Assess the fluency of the sentence: '{sentence}'. " \
           f"Give a score out of 10 for fluency and readability."
  response = model.generate_content(prompt) 
  try:
    score_str = re.search(r"Score: (\d+)", response.text).group(1)
    return int(score_str)
  except AttributeError:
    print(f"Could not extract score from response: {response.text}")
    return None

def analyze_confidence(avg_logprob):
  """
  Assesses the confidence level of the transcription based on avg_logprob.

  Args:
    avg_logprob: The average log probability of the transcription.

  Returns:
    A score out of 10 for confidence level.
  """
  if avg_logprob < -1.0:
    return 1
  elif -1.0 <= avg_logprob < -0.5:
    return 3
  elif -0.5 <= avg_logprob < 0:
    return 5
  elif 0 <= avg_logprob < 0.5:
    return 7
  else:
    return 10

# Example usage:
sentence = "To adopt the resource conversion conservation practices and follow the effectiveness management."
avg_logprob = -0.47946447

print("Grammar Score:", analyze_grammar(sentence))
# print("Vocabulary Score:", analyze_vocabulary(sentence))
# print("Pronunciation Score:", analyze_pronunciation(sentence))
# print("Fluency Score:", analyze_fluency(sentence))
print("Confidence Score:", analyze_confidence(avg_logprob))