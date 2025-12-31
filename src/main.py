from dotenv import load_dotenv
import os

from tts import TTS
from tiktok_video_generator import TikTokVideoGenerator

load_dotenv()

def main():
    VECTCUT_DIR = os.getenv("VECTCUT_DIR")
    VECTCUT_PORT = os.getenv("VECTCUT_PORT", "9001")
    BG_VIDEO = os.getenv("BG_VIDEO")
    
    STORY_FILE = os.getenv("STORY_FILE")
    NARRATOR_GENDER = os.getenv("NARRATOR_GENDER", "f")
    NARRATOR_VOICE = os.getenv("NARRATOR_VOICE", "heart")

    # Remove this later on
    SUBTITLES_SRT = os.getenv("SUBTITLES_SRT")

    if not STORY_FILE or not os.path.isfile(STORY_FILE):
            raise FileNotFoundError("STORY_FILE environment variable is not set or file does not exist.")
    if not BG_VIDEO or not os.path.isfile(BG_VIDEO):
            raise FileNotFoundError("BG_VIDEO environment variable is not set or file does not exist.")
    if not SUBTITLES_SRT or not os.path.isfile(SUBTITLES_SRT):
            raise FileNotFoundError("SUBTITLES_SRT environment variable is not set or file does not exist.")

    try:
        tts = TTS(result_folder="results", gender=NARRATOR_GENDER, voice=NARRATOR_VOICE)
        generator = TikTokVideoGenerator(api_url=f"http://localhost:{VECTCUT_PORT}", vectcut_dir=VECTCUT_DIR)

        print("Reading story text...")
        with open(STORY_FILE, "r", encoding="utf-8") as f:
            story_text = f.read()
        print("Generating voice audio from story text...")

        voice_audio_file_wav = tts.synthesize(story_text)
        voice_audio_file = tts.convert_wav_to_mp3(voice_audio_file_wav)

        print("Generating TikTok video project...")
        generator.create_project(width=1080, height=1920)

        print("Adding background video...")
        generator.add_background_video(video_path=BG_VIDEO, volume=0.05, speed=1.0, track_name="main")

        print("Adding voice audio...")
        generator.add_voice_audio(audio_path=voice_audio_file, volume=1.0, track_name="voice", target_start=0)

        print("Adding subtitles...")
        generator.add_subtitles(
            srt_url=SUBTITLES_SRT,
            font_size=30,
            font_color="#FFFFFF",
            transform_y=0
        )
        
        result = generator.save_and_import_to_capcut(auto_copy=True)

        if result.get("success"):
            print("TikTok video project generated and imported to CapCut successfully.")
        else:
            print(f"Failed to generate TikTok video project: {result.get('error')}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Troubleshooting:")
        print("- Ensure the VECTCUT_DIR, BG_VIDEO, VOICE_AUDIO, and SUBTITLES_SRT environment variables are set correctly.")
        print("- Ensure the VectCut API server is running")
        print("- Make sure all file paths are correct.")
        print("- Verify FFmpeg is available.")
        print("- Make sure CapCut is installed")

if __name__ == "__main__":
    main()