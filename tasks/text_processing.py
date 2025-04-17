import spacy
from langdetect import detect

# Пытаемся загрузить модели spaCy для русского и английского языков,
try:
    nlp_ru = spacy.load("ru_core_news_sm", disable=["parser", "ner"])
    nlp_en = spacy.load("en_core_web_sm", disable=["parser", "ner"])
except OSError:
    # Если модели не найдены, выводим сообщение об ошибке с инструкцией по установке
    raise Exception("Spacy models not found. Run:\n"
                    "python -m spacy download ru_core_news_sm\n"
                    "python -m spacy download en_core_web_sm")

# Функция предобработки текста
def preprocess(text):
    try:
        # Определяем язык текста (ru, en и т.п.)
        lang = detect(text)
    except:
        # В случае ошибки определения языка по умолчанию считаем текст английским
        lang = 'en'

    # В зависимости от языка обрабатываем текст соответствующей моделью spaCy
    if lang == 'ru':
        doc = nlp_ru(text.lower())
    else:
        doc = nlp_en(text.lower())

    # Извлекаем леммы из токенов, фильтруя ненужные:
    # пунктуацию, стоп-слова, числа, слишком короткие слова и неалфавитные токены
    lemmas = [
        token.lemma_.lower()
        for token in doc
        if not token.is_punct
           and not token.is_stop
           and not token.is_digit
           and len(token) > 2
           and token.is_alpha
    ]
    # Объединяем отфильтрованные леммы в одну строку
    return ' '.join(lemmas)
