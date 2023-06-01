from utils import load_dict, save_dict
from structlog import get_logger

log = get_logger()
CACHE_DIR = 'cache'

class ReverseIndex():
    def __init__(self):
        self.load_index()
    
    def load_index(self):
        # Load the saved model
        self.dic_texts = load_dict(f'{CACHE_DIR}/dic_texts.json')
        self.reverse_index = load_dict(f'{CACHE_DIR}/reverse_index.json')

    def search_words(self, list_words: list[str]):
        assert type(list_words)==list
        rev_index = self.reverse_index
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
        dic_related_websites, not_found = self.search_words(list_words=list_words)

        #threshold = 0.3
        filtered_websites = {k: v for k,v in dic_related_websites.items() if self.dic_texts.get(k) and self.dic_texts.get(k)['sentiment'] > threshold}
        limit_result = top_n
        return list(filtered_websites.keys())[:limit_result]

    def wn_search_word(self, word: str):
        from nltk.corpus import wordnet

        rev_index = self.reverse_index
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
        
        dic_related_urls, not_found = self.search_words(list_words=[best_synset])
        return dic_related_urls, not_found
    
    def get_dict_texts(self, s3_connection) -> dict:
        def get_model():
            import joblib
            model = joblib.load(f'{CACHE_DIR}/saved_model.pkl')
            vect  = joblib.load(f'{CACHE_DIR}/count_vectorizer.joblib')
            return model, vect

        def run_sentiment_anaysis(text: str, model, vect):
            sentiment = model.predict_proba(vect.transform([text]))[:, 1][0]
            # normalize from [0,1] to [-1,1]
            sentiment = 2*sentiment - 1
            return sentiment

        S3 = s3_connection
        FPATH_DIC_TEXTS = f'{CACHE_DIR}/dic_texts.json'
        dic_texts = load_dict(FPATH_DIC_TEXTS)
        model, vect = get_model()
 
        for s3_path in S3.list_files_recursive(folder='html_content/'):
            key = s3_path.split('.txt')[0]
            if key not in dic_texts:
                value = S3.read_html(fpath='html_content/'+s3_path)
                sentiment = run_sentiment_anaysis(text=value, model=model, vect=vect)
                dic_texts[key] = {'content': value, 'sentiment': sentiment}
        save_dict(dic_texts, FPATH_DIC_TEXTS)
        return dic_texts

    def build_reverse_index(self, s3_connection) -> None:
        from sklearn.feature_extraction.text import TfidfVectorizer
        import time
        start_time = time.time()
        dic_texts = self.get_dict_texts(s3_connection)
        time_to_get_dic = time.time() - start_time
        time_to_get_dic = f"{time_to_get_dic:.2f} seconds"
        #log.info(time_to_get_dic=time_to_get_dic)
        print(f"time_to_get_dic: {time_to_get_dic}")
        start_time = time.time()

        content_from_urls = [i['content'] for i in list(dic_texts.values())]
        website_urls      = list(dic_texts.keys())
        
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform(content_from_urls)

        res = {}

        for word in vectorizer.get_feature_names_out():
            j = vectorizer.vocabulary_[word]
            doc_df = {}
            
            for i in range(len(website_urls)):
                if tfidf[i,j] > 0:
                    doc_df[website_urls[i]] = tfidf[i,j]
                    
            res[word] = doc_df
        
        save_dict(res, f'{CACHE_DIR}/reverse_index.json')
        time_to_build_rev_idx = time.time() - start_time
        time_to_build_rev_idx = f"{time_to_build_rev_idx:.2f} seconds"
        #log.info(time_to_get_dic=time_to_get_dic)
        print(f"time_to_build_rev_idx: {time_to_build_rev_idx}")
        return None
