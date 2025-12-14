import spacy
import logging
import warnings

# Suppress "no word vectors" warning for small models
warnings.filterwarnings("ignore", message=r".*\[W007\].*")

logger = logging.getLogger(__name__)

# Cache models to avoid reloading
_nlp_en = None
_nlp_pt = None

def get_model(lang='pt'):
    global _nlp_en, _nlp_pt
    if lang == 'en':
        if _nlp_en is None:
            logger.info("Loading Spacy EN model (SM)...")
            try:
                _nlp_en = spacy.load("en_core_web_sm")
            except Exception as e:
                logger.error(f"Error loading EN model: {e}")
                return None
        return _nlp_en
    else:
        if _nlp_pt is None:
            logger.info("Loading Spacy PT model (SM)...")
            try:
                _nlp_pt = spacy.load("pt_core_news_sm")
            except Exception as e:
                logger.error(f"Error loading PT model: {e}")
                return None
        return _nlp_pt

import re

def detect_language(text):
    """
    Heuristic using stopword density.
    Compares coverage of EN vs PT common words.
    """
    if not text:
        return 'pt'
    
    # Clean punctuation and split
    text_clean = re.sub(r'[^\w\s]', '', text.lower())
    words = set(text_clean.split())
    
    # Common stopwords - Expanded list
    stops_en = {
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", 
        "it", "for", "not", "on", "with", "he", "as", "you", "do", "at", 
        "this", "but", "his", "by", "from", "they", "we", "say", "her", 
        "she", "or", "an", "will", "my", "one", "all", "would", "there", 
        "their", "what", "so", "up", "out", "if", "about", "who", "get", 
        "which", "go", "me", "is", "are", "was", "were", "been", "has", 
        "had", "did", "can", "could", "should", "would", "new", "us", 
        "including", "among", "after", "before", "during"
    }
    
    stops_pt = {
        "de", "a", "o", "que", "e", "do", "da", "em", "um", "para", 
        "com", "não", "uma", "os", "no", "se", "na", "por", "mais", 
        "as", "dos", "como", "mas", "ao", "ele", "das", "à", "seu", 
        "sua", "ou", "quando", "muito", "nos", "já", "eu", "também", 
        "só", "pelo", "pela", "até", "isso", "ela", "entre", "depois", 
        "sem", "mesmo", "aos", "ter", "seus", "quem", "nas", "me", 
        "foi", "foram", "era", "eram", "é", "são", "está", "estão"
    }
    
    # Count intersections
    score_en = len(words.intersection(stops_en))
    score_pt = len(words.intersection(stops_pt))
    
    # Bias slightly towards PT if tie/zero, but if EN > PT return EN
    if score_en > score_pt:
        return 'en'
    return 'pt'

def find_related_news(current_text, candidate_items, threshold=0.8, limit=3):
    """
    Finds news in candidate_items that are semantically similar to current_text.
    candidate_items: list of dicts (id, title, content, ...)
    """
    if not current_text:
        return []
    
    lang = detect_language(current_text)
    nlp = get_model(lang)
    
    if not nlp:
        return []

    doc_current = nlp(current_text)
    
    related = []
    
    for item in candidate_items:
        # Check title + description + content
        # For speed, maybe just title + description
        text = f"{item.get('title', '')} {item.get('description', '')}"
        if not text.strip():
            continue
            
        doc_candidate = nlp(text)
        similarity = doc_current.similarity(doc_candidate)
        
        if similarity >= threshold:
            related.append({
                "item": item,
                "score": similarity
            })
            
    # Sort by score desc
    related.sort(key=lambda x: x['score'], reverse=True)
    
    return [r['item'] for r in related[:limit]]
