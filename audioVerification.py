from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np
import sounddevice as sd
import time

class AdvancedVoiceVerification:
    def __init__(self, sample_duration=5, verification_interval=2, similarity_threshold=0.8):
        self.sample_duration = sample_duration
        self.verification_interval = verification_interval
        self.sample_rate = 16000
        self.encoder = VoiceEncoder()
        self.baseline_embedding = None
        self.similarity_threshold = similarity_threshold

    def record_audio(self, duration):
        print(f"Recording for {duration} seconds...")
        try:
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32
            )
            sd.wait()
            audio_data = audio_data.flatten() / np.max(np.abs(audio_data))
            return audio_data
        except sd.PortAudioError:
            print("[ERROR] Microphone not accessible.")
            return None

    def extract_embedding(self, audio):
        try:
            wav = preprocess_wav(audio, source_sr=self.sample_rate)
            embedding = self.encoder.embed_utterance(wav)
            return embedding
        except Exception as e:
            print(f"[ERROR] Failed to extract embedding: {e}")
            return None

    def capture_baseline(self):
        audio = self.record_audio(self.sample_duration)
        if audio is None or len(audio) == 0:
            print("[ERROR] No audio captured.")
            return False
        self.baseline_embedding = self.extract_embedding(audio)
        if self.baseline_embedding is not None:
            print("Baseline voice sample captured successfully.")
            return True
        return False

    def verify_voice(self, audio_chunk):
        current_embedding = self.extract_embedding(audio_chunk)
        if current_embedding is None:
            print("[ERROR] Failed to extract embedding for verification.")
            return False
        similarity = np.dot(
            self.baseline_embedding / np.linalg.norm(self.baseline_embedding),
            current_embedding / np.linalg.norm(current_embedding)
        )
        return similarity > self.similarity_threshold

    def monitor(self):
        print("Starting voice monitoring...")
        last_verify_time = time.time()

        def callback(indata, frames, time_info, status):
            nonlocal last_verify_time
            current_time = time.time()
            if current_time - last_verify_time < self.verification_interval:
                return

            if self.baseline_embedding is not None:
                audio_chunk = indata.flatten()
                is_valid = self.verify_voice(audio_chunk)
                if is_valid:
                    print("Voice match confirmed.")
                else:
                    print("Warning: Voice mismatch detected!")
                last_verify_time = current_time
            else:
                print("[ERROR] No baseline set. Record the baseline first.")

        with sd.InputStream(
            callback=callback,
            channels=1,
            samplerate=self.sample_rate,
            blocksize=int(self.sample_rate)
        ):
            try:
                while True:
                    sd.sleep(1000)
            except KeyboardInterrupt:
                print("\nMonitoring stopped.")

def main():
    verifier = AdvancedVoiceVerification(sample_duration=5, verification_interval=2, similarity_threshold=0.8)
    try:
        if verifier.capture_baseline():
            verifier.monitor()
    except KeyboardInterrupt:
        print("\nVoice verification system stopped.")

if __name__ == "__main__":
    main()
