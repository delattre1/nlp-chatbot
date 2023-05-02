from sklearn.feature_extraction.text import TfidfVectorizer
from utils import load_dict

#import joblib
#loaded_model = joblib.load(f'{CACHE_DIR}/saved_model.pkl')
#loaded_vect  = joblib.load(f'{CACHE_DIR}/count_vectorizer.joblib')

CACHE_DIR = 'cache'

class ReverseIndex():
    def __init__(self):
        self.load_index()
    
    def load_index(self):
        # Load the saved model
        self.dic_texts = load_dict(f'{CACHE_DIR}/dic_texts.json')
        self.reverse_index = load_dict(f'{CACHE_DIR}/reverse_index.json')

    def search_words(self, list_words: list[str], rev_index):
        assert type(list_words)==list
        result = {}
        not_found = []
        
        for word in list_words:
            word = word.lower()
            if word in rev_index.keys():
                for documento in rev_index[word].keys():
                    if documento not in result.keys():
                        result[documento]  = rev_index[word][documento]
                    else:
                        result[documento] += rev_index[word][documento]
            else:
                not_found.append(word)
        
        if result:
            sorted_res = dict(sorted(result.items(), key=lambda x: x[1], reverse=True))
            return sorted_res, not_found
        
        return {}, not_found

    def get_related_websites(self, list_words: list[str], threshold: int, top_n: int) -> list[str]:
        dic_related_websites, not_found = self.search_words(list_words=list_words, rev_index=self.reverse_index)

        #threshold = 0.3
        filtered_websites = {k: v for k,v in dic_related_websites.items() if self.dic_texts.get(k) and self.dic_texts.get(k)['sentiment'] > threshold}
        limit_result = top_n
        return list(filtered_websites.keys())[:limit_result]

    def wn_search_word(self, word: str, rev_index: dict) -> dict:
        # TODO:  install
        #from nltk.corpus import wordnet
        #!pip install nltk

        #import nltk
        #nltk.download('wordnet')
        #nltk.download('omw-1.4')

        best_synset, best_synset_wup = None, 0
        
        word = word.lower()
        
        synset_1 = wordnet.synsets(word, lang='por')
        if not synset_1:
            return None

        synset_1 = synset_1[0]

        for w in rev_index.keys():
            synset_2 = wordnet.synsets(w, lang='por')
            if not synset_2:
                continue
            
            synset_2 = synset_2[0]
            wup = synset_2.wup_similarity(synset_1)
            
            if wup > best_synset_wup:
                best_synset = w
                best_synset_wup = wup
        
        dic_related_urls, not_found = self.search_words(list_words=[best_synset], rev_index=rev_index)
        return dic_related_urls