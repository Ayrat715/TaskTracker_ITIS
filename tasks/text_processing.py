import spacy
from langdetect import detect

try:
    nlp_ru = spacy.load("ru_core_news_sm", disable=["parser", "ner"])
    nlp_en = spacy.load("en_core_web_sm", disable=["parser", "ner"])
except OSError:
    raise Exception("Spacy models not found. Run:\n"
                    "python -m spacy download ru_core_news_sm\n"
                    "python -m spacy download en_core_web_sm")

def preprocess(text):
    try:
        lang = detect(text)
    except:
        lang = 'en'

    if lang == 'ru':
        doc = nlp_ru(text.lower())
    else:
        doc = nlp_en(text.lower())

    lemmas = [
        token.lemma_.lower()
        for token in doc
        if not token.is_punct
           and not token.is_stop
           and not token.is_digit
           and len(token) > 2
           and token.is_alpha
    ]
    return ' '.join(lemmas)