def add_hashtags(title, hashtags, max_length=150):
    result = title.strip()

    if len(result) >= max_length:
        return result[:max_length]
    
    full_string = result + " " + hashtags.strip()

    if len(full_string) <= max_length:
        return full_string
    
    cropped = full_string[:max_length]

    last_space = cropped.rfind(' ')

    if last_space <= len(result):
        return result
    
    return cropped[:last_space]

def generate_caption(title, hashtags, max_length=150):
    return f"[FULL STORY] {add_hashtags(title, hashtags, max_length - len('[FULL STORY] '))}"
