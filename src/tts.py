from kokoro import KPipeline
import numpy as np
import soundfile as sf
import os
import subprocess

class TTS:
    def __init__(self, result_folder = "results", gender="f", voice=None):
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

        all_audio = []
        for (_, _, audio) in generator:
            all_audio.append(audio)

        combined_audio = np.concatenate(all_audio, axis=0)
        output_path = os.path.join(self.result_folder, "tts_output.wav")
        sf.write(output_path, combined_audio, samplerate=24000)
        return os.path.abspath(output_path)
    
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