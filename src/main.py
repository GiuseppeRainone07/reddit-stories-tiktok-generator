from dotenv import load_dotenv
import os

from tiktok_video_generator import TikTokVideoGenerator

load_dotenv()

def main():
    VECTCUT_DIR = os.getenv("VECTCUT_DIR")
    BG_VIDEO = os.getenv("BG_VIDEO")
    VOICE_AUDIO = os.getenv("VOICE_AUDIO")
    SUBTITLES_SRT = os.getenv("SUBTITLES_SRT")

    try:
        generator = TikTokVideoGenerator(api_url="http://localhost:9001", vectcut_dir=VECTCUT_DIR)

        print("Generating TikTok video project...")
        generator.create_project(width=1080, height=1920)

        print("Adding background video...")
        generator.add_background_video(video_path=BG_VIDEO, volume=0.2, speed=1.0, track_name="main")

        print("Adding voice audio...")
        generator.add_voice_audio(audio_path=VOICE_AUDIO, volume=1.0, track_name="voice", target_start=0)

        print("Adding subtitles...")
        generator.add_subtitles(
            srt_url=SUBTITLES_SRT,
            font_size=40,
            font_color="#FFFFFF",
            background_color="#000000",
            background_alpha=0.8
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