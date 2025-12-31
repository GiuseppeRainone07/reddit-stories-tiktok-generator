from kokoro import KPipeline
import soundfile as sf
import os
import subprocess

class TTS:
    def __init__(self, result_folder, gender="f", voice=None):
        os.makedirs(result_folder, exist_ok=True)
        if gender not in ["f", "m"]:
            raise ValueError("Gender must be 'f' or 'm'.")
        if voice is None:
            if gender == "f":
                voice = "heart"
            else:
                voice = "adam"
        self.gender = gender
        self.voice = voice
        self.result_folder = result_folder

    def synthesize(self, text, speed=1.15):
        pipeline = KPipeline(lang_code="a", repo_id='hexgrad/Kokoro-82M')
        generator = pipeline(text, voice=f"a{self.gender}_{self.voice}", speed=speed)
        for i, (_, _, audio) in enumerate(generator):
            filename = f"tts_output_{i}.wav"
            filepath = os.path.join(self.result_folder, filename)
            sf.write(filepath, audio, samplerate=24000)
            print(f"Generated audio saved to {filepath}")
        return os.path.abspath(filepath)
    
    def convert_wav_to_mp3(self, wav_file_path):
        # Convert WAV to MP3 using ffmpeg
        subprocess.run([
            "ffmpeg",
            "-y",          # overwrite output file if exists
            "-i", wav_file_path,
            "-codec:a", "libmp3lame",
            "-b:a", "192k",
            os.path.join(self.result_folder, "output.mp3")
        ], check=True)
        mp3_file_path = os.path.join(self.result_folder, "output.mp3")
        return os.path.abspath(mp3_file_path)

if __name__ == "__main__":
    tts = TTS()
    tts.synthesize("Hello, this is a text to speech synthesis test. Sounds pretty natural, right?")