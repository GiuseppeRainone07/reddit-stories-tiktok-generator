import json
import os
import shutil
import subprocess
import requests
import random

class TikTokVideoGenerator:
    def __init__(self, api_url="http://localhost:9001", vectcut_dir="vectcut"):
        self.api_url = api_url
        self.vectcut_dir = vectcut_dir
        self.draft_id = None

    def _make_request(self, endpoint, data):
        url = f"{self.api_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            if not result.get("success"):
                err = result.get("error", "Unknown error")
                raise Exception(f"API Error: {err}")
            return result.get("output", {})
        except requests.RequestException as e:
            raise Exception(f"Request to {endpoint} failed: {str(e)}")

    def create_project(self, width=1080, height=1920):
        response = self._make_request("create_draft", {
            "width": width,
            "height": height
        })

        self.draft_id = response.get("draft_id")
        print(f"Project created with Draft ID: {self.draft_id}")
        return self.draft_id
    
    def _get_video_duration(self, video_path):
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", video_path],
                capture_output=True,
                text=True,
                check=True
            )

            info = json.loads(result.stdout)
            duration = float(info["format"]["duration"])
            return duration
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get video duration: {str(e)}")
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            raise Exception(f"Error parsing ffprobe output: {str(e)}")

    def add_background_video(self, video_path, volume=0, speed=1.0, track_name="main", duration=None):
        if not self.draft_id:
            raise Exception("Draft ID is not set. Create a project first.")
        
        original_duration = self._get_video_duration(video_path)
        if duration is None:
            duration = original_duration - 5 # exclude first 5 seconds
        else:
            duration = min(duration, original_duration - 5)

        # Random start time calculation (to fit within original video duration)
        start = random.choices(range(5, int(original_duration - duration + 1)))[0]
        end = start + duration

        data = {
            "draft_id": self.draft_id,
            "video_url": video_path,
            "track_name": track_name,
            "speed": speed,
            "scale_x": 3.2, # Fixed scaling values for TikTok vertical format
            "scale_y": 3.2,
            "volume": volume,
            "target_start": 0,
            "relative_index": 0,
            "start": start,
            "end": end
        }

        if start is not None:
            data["start"] = start
        if end is not None:
            data["end"] = end
        
        response = self._make_request("add_video", data)

        print(f"Background video added successfully: {os.path.basename(video_path)}")
        return response, duration
    
    def add_initial_image(self, image_path, duration=3.0):
        if not self.draft_id:
            raise Exception("Draft ID is not set. Create a project first.")
        
        data = {
            "draft_id": self.draft_id,
            "image_url": image_path,
            "track_name": "reddit_frame",
            "scale_x": 0.8,
            "scale_y": 0.8,
            "start": 0,
            "end": duration,
            "relative_index": 0
        }

        response = self._make_request("add_image", data)
        print(f"Initial image added successfully: {os.path.basename(image_path)}")
        return response

    def add_audio(self, audio_path, start=0, end=None, target_start=0, volume=1.0, speed=1.0, track_name="voice"):
        if not self.draft_id:
            raise Exception("Draft ID is not set. Create a project first.")

        data = {
            "draft_id": self.draft_id,
            "audio_url": audio_path,
            "start": start,
            "target_start": target_start,
            "volume": volume,
            "speed": speed,
            "track_name": track_name
        }

        if end is not None:
            data["end"] = end

        response = self._make_request("add_audio", data)
        print(f"Voice audio added successfully: {os.path.basename(audio_path)}")
        return response
    
    def  add_subtitles(self, srt_url, time_offset=0, font="Nunito", font_size=5, font_color="#FFFFFF", transform_y=-0.8, scale=0.8):
        if not self.draft_id:
            raise Exception("Draft ID is not set. Create a project first.")
        
        data = {
            "draft_id": self.draft_id,
            "srt": srt_url,
            "time_offset": time_offset,
            "font": font,
            "font_size": font_size,
            "font_color": font_color,
            "transform_y": transform_y,
            "scale_x": scale,
            "scale_y": scale,
            "border_width": 70.0,
            "border_color": "#000000",
            "border_alpha": 1.0,
            "bold": True,
        }

        response = self._make_request("add_subtitle", data)
        print(f"Subtitles added successfully from: {os.path.basename(srt_url)}")
        return response
    
    def _find_draft_dir(self):
        if not self.vectcut_dir:
            raise Exception("VECTCUT_DIR is not set.")
        
        for it in os.listdir(self.vectcut_dir):
            if it.startswith("dfd_") and self.draft_id in it:
                return os.path.join(self.vectcut_dir, it)
            
        return None
    
    def save_draft(self, draft_dir=None):
        if not self.draft_id:
            raise Exception("Draft ID is not set. Create a project first.")
        
        data = {
            "draft_id": self.draft_id
        }

        if draft_dir:
            data["draft_folder"] = draft_dir
        
        response = self._make_request("save_draft", data)

        return response
    
    def save_and_import_to_capcut(self, auto_copy=True):
        if not self.draft_id:
            raise Exception("Draft ID is not set. Create a project first.")
        
        user_home = os.path.expanduser("~")
        capcut_draft_dir = os.path.join(user_home, "AppData", "Local", "CapCut", "User Data", "Projects", "com.lveditor.draft")

        if not os.path.exists(capcut_draft_dir):
            print(f"CapCut draft directory does not exist at {capcut_draft_dir}. Make sure CapCut is installed.")
            return {"success": False, "error": "CapCut draft directory not found."}

        print("Saving draft...")
        self.save_draft(os.path.join(capcut_draft_dir))
        
        draft_dir = self._find_draft_dir()
        if not draft_dir:
            print(f"⚠️ Warning: Could not find draft folder for {self.draft_id}")
            print(f"   Looking in: {self.vectcut_dir}")
            return {"success": False, "error": "Draft folder not found."}
        
        dest = os.path.join(capcut_draft_dir, os.path.basename(draft_dir))
        
        print(f"Draft folder located at: {draft_dir}")

        if auto_copy:
            print(f"Importing draft into CapCut...")
            try:
                if os.path.exists(dest):
                    shutil.rmtree(dest)
                shutil.copytree(draft_dir, dest)
                print(f"Draft imported to CapCut successfully at {dest}")

                return {"success": True, "imported_path": dest}
            except Exception as e:
                print(f"Failed to import draft to CapCut: {str(e)}")
                return {"success": False, "error": str(e)}
        else:
            print(f"Auto-copy disabled. Please manually copy the draft from {draft_dir} to {capcut_draft_dir}.")
            return {"success": True, "draft_path": draft_dir}
