from sc_client.client import search_link_contents_by_content_substrings, search_links_by_contents, search_links_by_contents_substrings, get_links_by_content

from natasha import Doc, Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger

segmenter = Segmenter()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
morph_vocab = MorphVocab()

def string_processing(text):
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    
    lemmatized_words = []
    
    for token in doc.tokens:
        if token.pos not in ['PUNCT', 'NUM', 'SYM'] and token.pos in ['NOUN', 'ADJ']:
            token.lemmatize(morph_vocab)
            lemmatized_words.append(token.lemma.lower())
    
    _links_list = []
    for _ in lemmatized_words:
        _link = search_links_by_contents(_)[0]
        print(f"LINK {get_links_by_content(_link)[0]}")
        _links_list.append(_link)
    print(_links_list)
    
    return lemmatized_words

if __name__ == "__main__":
    example_text = "Красивые гуси летят на юг"
    result = string_processing(example_text)
    print(result) 