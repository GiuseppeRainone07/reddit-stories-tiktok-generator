import re
from dotenv import load_dotenv
import os
import time

from tts import TTS
from tiktok_video_generator import TikTokVideoGenerator
from subtitles import Subtitles
from reddit_frame_image import RedditFrameImage
from reddit_story_fetcher import fetch_reddit_data
from caption import generate_caption

load_dotenv()

def test():
    REQUIRED_VARS = ["AVATAR_PATH", "VECTCUT_DIR", "BG_VIDEO"]
    for var_name in REQUIRED_VARS:
        if not os.getenv(var_name):
            raise EnvironmentError(f"{var_name} environment variable is not set.")
    
    NUM_OF_STORIES = int(os.getenv("NUM_OF_STORIES", "1"))
    USE_LINKS = os.getenv("USE_LINKS", "false").lower() == "true"
    
    processed_stories = 0

    for i in range(NUM_OF_STORIES):
        if USE_LINKS:
            STORY_LINK = os.getenv(f"STORY_LINK_{i+1}") if NUM_OF_STORIES > 1 else os.getenv("STORY_LINK")
            if not STORY_LINK:
                raise EnvironmentError("STORY_LINK environment variable is not set.")
            try:
                STORY_TITLE, story_text = fetch_reddit_data(STORY_LINK)
            except Exception:
                continue
        else:
            STORY_TITLE = os.getenv(f"STORY_TITLE_{i+1}") if NUM_OF_STORIES > 1 else os.getenv("STORY_TITLE")
            STORY_FILE = os.getenv(f"STORY_FILE_{i+1}") if NUM_OF_STORIES > 1 else os.getenv("STORY_FILE")
            print("Reading story text...")
            with open(STORY_FILE, "r", encoding="utf-8") as f:
                story_text = f.read()
            story_text = re.sub(r"\s*\r?\n\s*", " ", story_text).strip()

        NARRATOR_GENDER = os.getenv(f"NARRATOR_GENDER_{i+1}", "f") if NUM_OF_STORIES > 1 else os.getenv("NARRATOR_GENDER", "f")
        NARRATOR_VOICE = os.getenv(f"NARRATOR_VOICE_{i+1}", "heart") if NUM_OF_STORIES > 1 else os.getenv("NARRATOR_VOICE", "heart")

        print("STORY TITLE:", STORY_TITLE)
        print("NARRATOR: ", NARRATOR_GENDER, NARRATOR_VOICE)
        print("STORY TEXT:", story_text[:100] + "..." if len(story_text) > 100 else story_text)
        processed_stories += 1
    
    print(f"Successfully processed {processed_stories} stories.")

def main():
    start = time.perf_counter()

    REQUIRED_VARS = ["AVATAR_PATH", "VECTCUT_DIR", "BG_VIDEO"]
    for var_name in REQUIRED_VARS:
        if not os.getenv(var_name):
            raise EnvironmentError(f"{var_name} environment variable is not set.")

    RESULTS_DIR = os.getenv("RESULTS_DIR", "results")

    NUM_OF_STORIES = int(os.getenv("NUM_OF_STORIES", "1"))
    USE_LINKS = os.getenv("USE_LINKS", "false").lower() == "true"

    HASHTAGS = "#fyp #foryou #reddit #redditstories #fullystory #storytime #redditreadings #reddit_tiktok"

    POSTFULLY_URL = os.getenv("POSTFULLY_URL", "https://postfully.app/tools/reddit-post-template/")
    AVATAR_PATH = os.getenv("AVATAR_PATH")

    VECTCUT_DIR = os.getenv("VECTCUT_DIR")
    VECTCUT_PORT = os.getenv("VECTCUT_PORT", "9001")
    BG_VIDEO = os.getenv("BG_VIDEO")

    try:
        subtitles_generator = Subtitles(result_folder=RESULTS_DIR, device="cpu", compute_type="int8")
        generator = TikTokVideoGenerator(api_url=f"http://localhost:{VECTCUT_PORT}", vectcut_dir=VECTCUT_DIR)
        reddit_frame_image_generator = RedditFrameImage(postfully_url=POSTFULLY_URL, avatar_path=AVATAR_PATH, result_folder=RESULTS_DIR)
    except Exception as e:
        print(f"Failed to initialize components: {str(e)}")
        return
    
    os.makedirs(RESULTS_DIR, exist_ok=True)

    captions = []

    for i in range(NUM_OF_STORIES):
        if USE_LINKS:
            STORY_LINK = os.getenv(f"STORY_LINK_{i+1}") if NUM_OF_STORIES > 1 else os.getenv("STORY_LINK")
            if not STORY_LINK:
                raise EnvironmentError("STORY_LINK environment variable is not set.")
            try:
                STORY_TITLE, story_text = fetch_reddit_data(STORY_LINK)
            except Exception:
                continue
        else:
            STORY_TITLE = os.getenv(f"STORY_TITLE_{i+1}") if NUM_OF_STORIES > 1 else os.getenv("STORY_TITLE")
            STORY_FILE = os.getenv(f"STORY_FILE_{i+1}") if NUM_OF_STORIES > 1 else os.getenv("STORY_FILE")
            print("Reading story text...")
            with open(STORY_FILE, "r", encoding="utf-8") as f:
                story_text = f.read()
            story_text = re.sub(r"\s*\r?\n\s*", " ", story_text).strip()

        NARRATOR_GENDER = os.getenv(f"NARRATOR_GENDER_{i+1}", "f") if NUM_OF_STORIES > 1 else os.getenv("NARRATOR_GENDER", "f")
        NARRATOR_VOICE = os.getenv(f"NARRATOR_VOICE_{i+1}", "heart" if NARRATOR_GENDER == "f" else "adam") if NUM_OF_STORIES > 1 else os.getenv("NARRATOR_VOICE", "heart" if NARRATOR_GENDER == "f" else "adam")

        try:
            print(f"Starting generation for TikTok video ({i+1}) {STORY_TITLE}:\n")

            tts = TTS(result_folder=RESULTS_DIR, gender=NARRATOR_GENDER, voice=NARRATOR_VOICE)
            print("Generating voice audio from story title and text...")

            title_audio_file_wav, title_audio_duration = tts.synthesize(STORY_TITLE, name="title")
            title_audio_file_wav, title_audio_duration = tts.trim_silence(title_audio_file_wav)
            title_audio_file = tts.convert_wav_to_mp3(title_audio_file_wav)

            voice_audio_file_wav, voice_audio_duration = tts.synthesize(story_text, name="voice")
            voice_audio_file_wav, voice_audio_duration = tts.trim_silence(voice_audio_file_wav)
            voice_audio_file = tts.convert_wav_to_mp3(voice_audio_file_wav)

            mid_silence_duration = 0.4  # seconds

            initial_image_path = reddit_frame_image_generator.download_frame_image(text=STORY_TITLE)

            print("Generating TikTok video project...")
            generator.create_project(width=1080, height=1920)

            print("Adding background video...")
            generator.add_background_video(video_path=BG_VIDEO, volume=0, speed=1.0, track_name="main", duration=title_audio_duration + voice_audio_duration + mid_silence_duration)

            print("Adding initial image...")
            generator.add_initial_image(image_path=initial_image_path, duration=title_audio_duration)

            print("Adding ding sound...")
            ding_path = os.path.abspath(os.path.join("static", "ding.wav"))
            generator.add_audio(audio_path=ding_path, volume=1.0, track_name="ding", target_start=0)

            print("Adding title audio...")
            generator.add_audio(audio_path=title_audio_file, volume=1.0, track_name="title", target_start=0)

            print("Adding voice audio...")
            generator.add_audio(audio_path=voice_audio_file, volume=1.0, track_name="voice", target_start=title_audio_duration + mid_silence_duration)

            subs = subtitles_generator.transcribe(voice_audio_file_wav)
            subs_srt = os.path.join(RESULTS_DIR, "subtitles.srt")
            subtitles_generator.generate_srt(subs, subs_srt, words_per_subtitle=1, audio_duration=voice_audio_duration)
            print("Adding subtitles...")
            generator.add_subtitles(
                srt_url=subs_srt,
                font_size=36,
                font_color="#FFFFFF",
                transform_y=-0.05,
                time_offset=title_audio_duration + mid_silence_duration,
            )

            result = generator.save_and_import_to_capcut(auto_copy=True)

            if result.get("success"):
                print("TikTok video project generated and imported to CapCut successfully.")
            else:
                print(f"Failed to generate TikTok video project: {result.get('error')}")

            caption = generate_caption(STORY_TITLE, HASHTAGS, max_length=150)
            captions.append(caption)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Troubleshooting:")
            print(f"- Ensure the required environment variables are set correctly: {', '.join(REQUIRED_VARS)}")
            print("- Ensure the VectCut API server is running")
            print("- Make sure all file paths are correct.")
            print("- Verify FFmpeg is available.")
            print("- Make sure CapCut is installed")

    end = time.perf_counter()
    print(f"Total execution time: {end - start:.2f} seconds")
    
    print("\nGenerated Captions:")
    for i, caption in enumerate(captions, 1):
        print(f"Video {i} Caption: {caption}")

if __name__ == "__main__":
    main()