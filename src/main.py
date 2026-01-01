from dotenv import load_dotenv
import os

from tts import TTS
from tiktok_video_generator import TikTokVideoGenerator
from subtitles import Subtitles
from reddit_frame_image import RedditFrameImage

load_dotenv()

def main():
    REQUIRED_VARS = ["AVATAR_PATH", "VECTCUT_DIR", "STORY_FILE", "BG_VIDEO", "STORY_TITLE"]
    for var_name in REQUIRED_VARS:
        if not os.getenv(var_name):
            raise EnvironmentError(f"{var_name} environment variable is not set.")

    RESULTS_DIR = os.getenv("RESULTS_DIR", "results")

    POSTFULLY_URL = os.getenv("POSTFULLY_URL", "https://postfully.app/tools/reddit-post-template/")
    AVATAR_PATH = os.getenv("AVATAR_PATH")
    STORY_TITLE = os.getenv("STORY_TITLE")

    VECTCUT_DIR = os.getenv("VECTCUT_DIR")
    VECTCUT_PORT = os.getenv("VECTCUT_PORT", "9001")
    BG_VIDEO = os.getenv("BG_VIDEO")
    
    STORY_FILE = os.getenv("STORY_FILE")
    NARRATOR_GENDER = os.getenv("NARRATOR_GENDER", "f")
    NARRATOR_VOICE = os.getenv("NARRATOR_VOICE", "heart")

    os.makedirs(RESULTS_DIR, exist_ok=True)

    try:
        tts = TTS(result_folder=RESULTS_DIR, gender=NARRATOR_GENDER, voice=NARRATOR_VOICE)
        subtitles_generator = Subtitles(result_folder=RESULTS_DIR, device="cpu", compute_type="int8")
        generator = TikTokVideoGenerator(api_url=f"http://localhost:{VECTCUT_PORT}", vectcut_dir=VECTCUT_DIR)
        reddit_frame_image_generator = RedditFrameImage(postfully_url=POSTFULLY_URL, avatar_path=AVATAR_PATH, result_folder=RESULTS_DIR)

        print("Reading story text...")
        with open(STORY_FILE, "r", encoding="utf-8") as f:
            story_text = f.read()
        print("Generating voice audio from story text...")

        voice_audio_file_wav = tts.synthesize(story_text)
        voice_audio_file = tts.convert_wav_to_mp3(voice_audio_file_wav)
        initial_image_path = reddit_frame_image_generator.download_frame_image(text=STORY_TITLE)

        print("Generating TikTok video project...")
        generator.create_project(width=1080, height=1920)

        print("Adding background video...")
        print("Adding initial image...")
        generator.add_initial_image(image_path=initial_image_path, duration=title_audio_duration)

        print("Adding ding sound...")
        ding_path = os.path.abspath(os.path.join("static", "ding.wav"))
        generator.add_audio(audio_path=ding_path, volume=1.0, track_name="ding", target_start=0)

        print("Adding voice audio...")
        generator.add_voice_audio(audio_path=voice_audio_file, volume=1.0, track_name="voice", target_start=0)

        subs = subtitles_generator.transcribe(voice_audio_file_wav)
        subs_srt = os.path.join(RESULTS_DIR, "subtitles.srt")
        subtitles_generator.generate_srt(subs, subs_srt, words_per_subtitle=1)

        print("Adding subtitles...")
        generator.add_subtitles(
            srt_url=subs_srt,
            font_size=36,
            font_color="#FFFFFF",
            transform_y=-0.2,
        )
        
        result = generator.save_and_import_to_capcut(auto_copy=True)

        if result.get("success"):
            print("TikTok video project generated and imported to CapCut successfully.")
        else:
            print(f"Failed to generate TikTok video project: {result.get('error')}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Troubleshooting:")
        print(f"- Ensure the required environment variables are set correctly: {', '.join(REQUIRED_VARS)}")
        print("- Ensure the VectCut API server is running")
        print("- Make sure all file paths are correct.")
        print("- Verify FFmpeg is available.")
        print("- Make sure CapCut is installed")

if __name__ == "__main__":
    main()