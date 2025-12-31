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
    def __init__(self):
        self.model = whisperx.load_model("base", device="cpu", compute_type="int8")
        self.align_model, self.metadata = whisperx.load_align_model(language_code="en", device="cpu")

    def transcribe(self, audio_path):
        audio = whisperx.load_audio(audio_path)
        
        result = self.model.transcribe(audio_path, batch_size=16, language="en")
        result = whisperx.align(result["segments"], self.align_model, self.metadata, audio, device="cpu")

        for segment in result["segments"]:
            for word in segment["words"]:
                print(f"{word['word']}: {word['start']:.2f}s - {word['end']:.2f}s")
        
        return result


if __name__ == "__main__":
    subtitles = Subtitles()
    AUDIO_FILE = os.getenv("AUDIO_FILE")
    if not AUDIO_FILE or not os.path.isfile(AUDIO_FILE):
            raise FileNotFoundError("AUDIO_FILE environment variable is not set or file does not exist.")
    with open(AUDIO_FILE, "r", encoding="utf-8") as f:
        story_text = f.read()
    print("Performing transcription and alignment...")
    subtitles.transcribe("results/tts_output_0.wav")
    print("Done.")
