import os
import subprocess
import json
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Replace with your API key and URL (Avoid exposing sensitive keys in code)
api_key = "XruZ4YShquS2ny9g98e1Tl3tB8EGJemx9XRVgFgEi_za"
url = "https://api.au-syd.speech-to-text.watson.cloud.ibm.com/instances/d8cd3f9f-b1e7-4c26-b90a-030158ff1bc9"

# Authenticate with IBM Watson
authenticator = IAMAuthenticator(api_key)
speech_to_text = SpeechToTextV1(authenticator=authenticator)
speech_to_text.set_service_url(url)

# If the audio file is in FLAC format, convert it to MP3
audio_file = "audio-file.flac"
mp3_file = "audio-file.mp3"

# Check if the file is already in mp3 format, otherwise convert
if not os.path.exists(mp3_file):
    command = f'ffmpeg -i {audio_file} -vn -ar 44100 -ac 2 -b:a 192k {mp3_file}'
    # print(f'Running command: {command}')  # Debug: print the conversion command
    subprocess.call(command, shell=True)
    if os.path.exists(mp3_file):
        print(f"Converted {audio_file} to {mp3_file}")
    else:
        print(f"Failed to convert {audio_file} to {mp3_file}")
else:
    print(f"{mp3_file} already exists. Skipping conversion.")

# Find the mp3 files in the current directory
files = [filename for filename in os.listdir('.') if filename.endswith(".mp3")]
print("MP3 files found:", files)

# Initialize results list
results = []

# Process each mp3 file
for filename in files:
    try:
        with open(filename, 'rb') as audio_file:
            response = speech_to_text.recognize(
                audio=audio_file,
                content_type='audio/mp3',  # Specify the content type for MP3 files
                model='en-AU_NarrowbandModel',  # Change model as needed
                # continuous=True,
                inactivity_timeout=360
            ).get_result()
        
        results.append(response)
        # print(results)
        print(f"Transcription for {filename}:", response['results'][0]['alternatives'][0]['transcript'])
    
    except Exception as e:
        print(f"Error processing {filename}: {e}")

# Optionally save results to a JSON file
with open("transcription_results.json", "w") as outfile:
    json.dump(results, outfile, indent=4)
