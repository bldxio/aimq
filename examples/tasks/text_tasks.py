"""
Text processing workflows for demonstration.
"""
from langchain_core.runnables import chain

@chain
def uppercase_text(data: dict) -> dict:
    """Convert input text to uppercase."""
    text = data.get('text', '')
    return {'result': text.upper()}

@chain
def text_statistics(data: dict) -> dict:
    """Calculate basic statistics about the input text."""
    text = data.get('text', '')
    words = text.split()
    
    results = {
        'word_count': len(words),
        'char_count': len(text),
        'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0
    }
    return results
