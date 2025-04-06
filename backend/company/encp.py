import random
import string
# import pycryptodom
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import hashlib
import os



interview_db = {}

generated_interview_ids = set()

def generate_unique_VIVA_id():
   
    characters = "1234567890" + string.ascii_uppercase  
    while True:
        interview_id = ''.join(random.choices(characters, k=6))
        if interview_id not in generated_interview_ids:
            generated_interview_ids.add(interview_id)
            return interview_id

def post_interview(interviewer_name, interview_title):
    interview_id = generate_unique_VIVA_id() 
    # Store the interview details in the database
    interview_db[interview_id] = {
        "interviewer": interviewer_name,
        "title": interview_title
    }
    
    print(f"Interview '{interview_title}' by {interviewer_name} posted successfully!")
    print(f"Generated Interview ID: {interview_id}")
    return interview_id


secret_key = hashlib.sha256(b"your-fixed-key").digest()  # Generates a 32-byte key



def encrypt_and_shorten_student_id(student_id):

    cipher = AES.new(secret_key, AES.MODE_CBC)
    iv = cipher.iv  # Initialization vector
    encrypted_id = cipher.encrypt(pad(student_id.encode(), AES.block_size))

    encrypted_data = iv + encrypted_id  # IV is prepended to ciphertext

    # Hash the encrypted data for shortening
    hash_of_encrypted_data = hashlib.sha256(encrypted_data).digest()

    # Base64 encode the hash and truncate to 8–10 characters
    shortened_id = base64.urlsafe_b64encode(hash_of_encrypted_data).decode()[:10]

    # Store full encrypted data for decryption (in practice, store securely in DB)
    full_encrypted_data = base64.urlsafe_b64encode(encrypted_data).decode()

    return full_encrypted_data


def decrypt_student_id(full_encrypted_data):
    # Decode the Base64-encoded full encrypted data
    encrypted_data = base64.urlsafe_b64decode(full_encrypted_data)

    # Extract the IV (first 16 bytes) and encrypted ID
    iv = encrypted_data[:16]
    encrypted_id = encrypted_data[16:]

    # Decrypt using AES
    cipher = AES.new(secret_key, AES.MODE_CBC, iv=iv)
    decrypted_id = unpad(cipher.decrypt(encrypted_id), AES.block_size)

    return decrypted_id.decode()






