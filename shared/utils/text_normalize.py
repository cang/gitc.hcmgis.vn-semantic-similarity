import re
import unicodedata
from pyvi.ViTokenizer import tokenize

def preprocess_vi(text: str) -> str:
    '''
    RAW TEXT
     ↓
    Unicode normalize
     ↓
    Trim / whitespace
     ↓
    Lowercase
     ↓
    Chuẩn hóa dấu câu
     ↓
    Chuẩn hóa số / ký hiệu
     ↓
    Sentence length control
     ↓
    (OPTIONAL) Vietnamese word segmentation
     ↓
    Embedding
    '''
    if not text:
        return text
        
    print(f"origin text: {text}")        
    text = unicodedata.normalize("NFC", text)
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[!?]{2,}", "!", text)
    text = re.sub(r"[.]{2,}", ".", text)    
    text = tokenize(text)
    print(f"preprocess text: {text}")
    return text