import requests

def fetch_reddit_data(url: str):
    if not url.startswith("http"):
        raise ValueError("Invalid URL provided.")
    headers = { "User-Agent": "User-Agent': 'python:reddit_fetcher:v1.0 (by /u/lllAlexxinolll)" }
    response = requests.get(f"{url}.json", headers=headers)
    if response.status_code != 200:
        raise ConnectionError(f"Failed to fetch data from Reddit. Status code: {response.status_code}")
    data = response.json()
    post_data = data[0]['data']['children'][0]['data']
    title = post_data.get('title', '')
    text = post_data.get('selftext', '')
    return title, text

if __name__ == "__main__":
    test_url = "https://www.reddit.com/r/confession/comments/1q10oab/my_dad_doesnt_know_hes_not_my_dadand_never_will"
    try:
        title, text = fetch_reddit_data(test_url)
        print("Title:", title)
        print("Text:", text)
    except Exception as e:
        print(f"An error occurred: {e}")