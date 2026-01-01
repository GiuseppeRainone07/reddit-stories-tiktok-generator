import whisperx
import torch
import os

# Monkey-patch torch.load to use weights_only=False for compatibility
_original_torch_load = torch.load

def patched_torch_load(*args, **kwargs):
    # Force weights_only=False to allow loading older checkpoints
    kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)

torch.load = patched_torch_load

class Subtitles:
    def __init__(self, result_folder="results", device="cpu", compute_type="int8"):
        self.result_folder = result_folder
        self.device = device
        self.compute_type = compute_type
        self.model = whisperx.load_model("base", device=self.device, compute_type=self.compute_type)
        self.align_model, self.metadata = whisperx.load_align_model(language_code="en", device=self.device)

    def transcribe(self, audio_path):
        audio = whisperx.load_audio(audio_path)
        
        result = self.model.transcribe(audio_path, batch_size=16, language="en")
        result = whisperx.align(result["segments"], self.align_model, self.metadata, audio, device=self.device)
        
        return result
    
    def _format_timestamp(self, seconds):
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"
    
    def generate_srt(self, result, output_path, words_per_subtitle=5):
        with open(output_path, "w", encoding="utf-8") as f:
            subtitle_index = 1

            all_words = []
            for segment in result["segments"]:
                if "words" in segment:
                    all_words.extend(segment["words"])

            i = 0
            while i < len(all_words):
                words_group = all_words[i:i + words_per_subtitle]

                if not words_group:
                    break

                start_time = words_group[0]["start"]
                
                if i + words_per_subtitle < len(all_words):
                    end_time = all_words[i + words_per_subtitle]["start"]
                else:
                    end_time = words_group[-1]["end"]

                text = " ".join([w["word"] for w in words_group])

                f.write(f"{subtitle_index}\n")
                f.write(f"{self._format_timestamp(start_time)} --> {self._format_timestamp(end_time)}\n")
                f.write(f"{text}\n\n")

                subtitle_index += 1
                i += words_per_subtitle

        print(f"SRT file generated at: {output_path}")


if __name__ == "__main__":
    subtitles = Subtitles()
    AUDIO_FILE = os.getenv("AUDIO_FILE")
    print("AUDIO_FILE:", AUDIO_FILE)
    if not AUDIO_FILE or not os.path.isfile(AUDIO_FILE):
        raise FileNotFoundError("AUDIO_FILE environment variable is not set or file does not exist.")
    print("Performing transcription and alignment...")
    result = subtitles.transcribe(AUDIO_FILE)
    subtitles.generate_srt(result, "output.srt")
    print("Done.")
