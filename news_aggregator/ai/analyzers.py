import spacy
import logging

logger = logging.getLogger(__name__)

# Cache models to avoid reloading
_nlp_en = None
_nlp_pt = None

def get_model(lang='pt'):
    global _nlp_en, _nlp_pt
    if lang == 'en':
        if _nlp_en is None:
            logger.info("Loading Spacy EN model...")
            try:
                _nlp_en = spacy.load("en_core_web_md")
            except Exception as e:
                logger.error(f"Error loading EN model: {e}")
                return None
        return _nlp_en
    else:
        if _nlp_pt is None:
            logger.info("Loading Spacy PT model...")
            try:
                _nlp_pt = spacy.load("pt_core_news_md")
            except Exception as e:
                logger.error(f"Error loading PT model: {e}")
                return None
        return _nlp_pt

def detect_language(text):
    """
    Very simple heuristic. 
    Ideal would be using 'langdetect' library.
    """
    if not text:
        return 'pt'
    
    text_lower = text.lower()
    # Common words
    if " the " in text_lower or " of " in text_lower or " and " in text_lower:
        return 'en'
    return 'pt'

def find_related_news(current_text, candidate_items, threshold=0.7, limit=3):
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
