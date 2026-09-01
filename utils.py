import re

def clean_file_name(file_name: str) -> str:
    file_name = re.sub(r"http\S+|www\.\S+", "", file_name)
    file_name = re.sub(r"[@_]", " ", file_name)
    file_name = re.sub(r"\s+", " ", file_name).strip()
    return file_name
  
