import re
from kokoro import KPipeline
import numpy as np
import soundfile as sf
import os
import subprocess
from pydub import AudioSegment
from pydub.silence import detect_leading_silence
from replacements import CURSE_WORDS_PATTERN, PATTERN, ABBREVIATIONS

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

    def trim_silence(self, audio_path, output_path=None, silence_threshold=-50.0):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Input audio file not found: {audio_path}")
        
        input_ext = os.path.splitext(audio_path)[1].lower().lstrip('.')

        if output_path is None:
            output_path = audio_path.replace(f".{input_ext}", f"_trimmed.{input_ext}")
        
        sound = AudioSegment.from_file(audio_path, format=input_ext)

        start_trim = detect_leading_silence(sound, silence_threshold=silence_threshold)
        end_trim = detect_leading_silence(sound.reverse(), silence_threshold=silence_threshold)

        duration = len(sound)
        trimmed_sound = sound[start_trim:duration - end_trim]

        trimmed_sound.export(output_path, format=input_ext)

        return output_path, len(trimmed_sound) / 1000.0  # duration in seconds
    
    def add_fade(self, audio_path, output_path=None, fade_in_duration=500, fade_out_duration=500):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Input audio file not found: {audio_path}")
        
        input_ext = os.path.splitext(audio_path)[1].lower().lstrip('.')

        if output_path is None:
            output_path = audio_path.replace(f".{input_ext}", f"_faded.{input_ext}")
        
        sound = AudioSegment.from_file(audio_path, format=input_ext)

        audio_duration = len(sound)

        fade_in_duration = min(fade_in_duration, audio_duration // 2)
        fade_out_duration = min(fade_out_duration, audio_duration // 2)
        faded_sound = sound
        if fade_in_duration > 0:
            faded_sound = faded_sound.fade_in(fade_in_duration)
        if fade_out_duration > 0:
            faded_sound = faded_sound.fade_out(fade_out_duration)

        export_params = {}
        
        if input_ext == 'wav':
            # WAV: Use high bitrate and sample width
            export_params = {
                'format': 'wav',
                'parameters': ['-acodec', 'pcm_s16le']  # 16-bit PCM (lossless)
            }
        elif input_ext == 'mp3':
            # MP3: Use highest quality
            export_params = {
                'format': 'mp3',
                'bitrate': '320k',  # Maximum MP3 bitrate
                'parameters': ['-q:a', '0']  # Highest quality
            }
        else:
            export_params = {'format': input_ext}
        
        faded_sound.export(output_path, **export_params)

        return output_path

    def _expand_abbreviations(self, text):
        def replacer(match):
            abbr = match.group(0)
            full = ABBREVIATIONS.get(abbr.lower())
            if abbr.isupper():
                return full.upper()
            elif abbr.istitle():
                return full.title()
            else:
                return full
        return CURSE_WORDS_PATTERN.sub(replacer, PATTERN.sub(replacer, text))

    def synthesize(self, text, speed=1.15, name="output"):
        text = self._expand_abbreviations(text)
        pipeline = KPipeline(lang_code="a", repo_id='hexgrad/Kokoro-82M')
        generator = pipeline(text, voice=f"a{self.gender}_{self.voice}", speed=speed)

        all_audio = []
        for (_, _, audio) in generator:
            all_audio.append(audio)

        combined_audio = np.concatenate(all_audio, axis=0)
        output_path = os.path.join(self.result_folder, f"{name}.wav")
        sf.write(output_path, combined_audio, samplerate=24000)
        return os.path.abspath(output_path), sf.info(output_path).duration
    
    def convert_wav_to_mp3(self, wav_file_path):
        filename = os.path.basename(wav_file_path)
        name, _ = os.path.splitext(filename)
        # Convert WAV to MP3 using ffmpeg
        subprocess.run([
            "ffmpeg",
            "-y",          # overwrite output file if exists
            "-i", wav_file_path,
            "-codec:a", "libmp3lame",
            "-b:a", "192k",
            os.path.join(self.result_folder, f"{name}.mp3")
        ], check=True)
        mp3_file_path = os.path.join(self.result_folder, f"{name}.mp3")
        return os.path.abspath(mp3_file_path)

if __name__ == "__main__":
    tts = TTS()
    tts.convert_wav_to_mp3("./static/ding.wav")