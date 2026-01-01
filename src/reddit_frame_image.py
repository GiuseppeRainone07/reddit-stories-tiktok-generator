import os
from playwright.sync_api import sync_playwright

class RedditFrameImage:
    def __init__(self, postfully_url, avatar_path, result_folder):
        self.postfully_url = postfully_url
        self.avatar_path = avatar_path
        self.result_folder = result_folder

    def download_frame_image(self, text, upvotes=67000, comments=4100):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            page.goto(self.postfully_url)

            page.wait_for_load_state("networkidle")

            avatar_input = page.locator("input[name='avatar']")
            avatar_input.set_input_files(self.avatar_path)

            username_input = page.locator("input[name='username']")
            username_input.fill("Massive Ideas")

            text_input = page.locator("textarea[name='text']")
            text_input.fill(text)

            upvotes_input = page.locator("input[name='upvoteCount']")
            upvotes_input.fill(str(upvotes))

            comments_input = page.locator("input[name='commentCount']")
            comments_input.fill(str(comments))

            generate_button = page.locator("button:has-text('Download')")
            
            with page.expect_download() as download_info:
                generate_button.click()

            download = download_info.value
            filepath = os.path.join(self.result_folder, "reddit_frame_image.png")
            download.save_as(filepath)

            browser.close()
        return filepath

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    RESULTS_DIR = os.getenv("RESULTS_DIR", "results")
    POSTFULLY_URL = os.getenv("POSTFULLY_URL", "https://postfully.app/tools/reddit-post-template/")
    AVATAR_PATH = os.getenv("AVATAR_PATH", "avatar.png")

    os.makedirs(RESULTS_DIR, exist_ok=True)

    reddit_frame_image = RedditFrameImage(postfully_url=POSTFULLY_URL, avatar_path=AVATAR_PATH, result_folder=RESULTS_DIR)
    result_image_path = reddit_frame_image.download_frame_image(
        text="This is an example Reddit post generated using Playwright automation.",
        upvotes=12345,
        comments=678
    )
    print(f"Reddit frame image saved at: {result_image_path}")