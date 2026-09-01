import re
import aiohttp
from difflib import get_close_matches

def clean_file_name(text: str) -> str:
    if not text:
        return "Unknown File"
    
    text = re.sub(r'(https?://)?(www\.)?(t\.me|telegram\.me)/\S+', '', text)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", 
        flags=re.UNICODE
    )
    text = emoji_pattern.sub('', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text if text else "Cleaned File"

async def get_spelling_suggestion(query: str, all_titles_list: list) -> str:
    clean_q = clean_file_name(query).lower()
    matches = get_close_matches(clean_q, [t.lower() for t in all_titles_list], n=1, cutoff=0.5)
    if matches:
        return matches[0]
    
    url = f"http://suggestqueries.google.com/complete/search?client=firefox&q={clean_q}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=2)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if len(data) > 1 and len(data[1]) > 0:
                        return data[1][0]
    except Exception:
        pass
    return None

def get_google_search_url(query: str) -> str:
    encoded_query = query.replace(" ", "+")
    return f"https://www.google.com/search?q={encoded_query}"
    
