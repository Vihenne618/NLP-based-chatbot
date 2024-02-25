import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet
from collections import OrderedDict

# nltk.download('punkt')
# nltk.download ('stopwords')
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('universal_tagset')
# nltk.download('webtext')

# customize the stop word list
stopwords = [   'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 
    'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 
    'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 
    'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 
    'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'all', 'any', 
    'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 
    'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', 
    "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', 
    "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', 
    "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', 
    "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
]

# Preprocessing user input
def preprocess_input(input_text):
    return process_text(input_text)

# Process texts of the sentence
def process_text_list(input_text_list):
    if(len(input_text_list) != 0):
        result = []
        for input_text in input_text_list:
            result.append(process_text(input_text))
        return result
    return input_text_list

# Process the text of the sentence
def process_text(input_text):
    # Remove special characters and extra Spaces from text
    input_text = re.sub(r'[^a-zA-Z0-9\s]', '', input_text)
    input_text = re.sub(r'\s+', ' ', input_text)
    # Lowercasing
    input_text = input_text.lower()
    # Tokenization
    tokens = word_tokenize(input_text)
    # stopword removal
    tokens_without_sw =  [word.lower() for word in tokens if not word in stopwords]
    # Lemmatization
    lemmatiser = WordNetLemmatizer()
    posmap = {'ADJ': 'a','ADV': 'r','NOUN': 'n','VERB': 'v'}
    post = nltk.pos_tag(tokens_without_sw, tagset='universal')
    lemmas_sent = []
    for word, pos_tag in post:
        wordnet_pos = posmap.get(pos_tag,None)
        lemma = lemmatiser.lemmatize(word, pos=wordnet_pos) if wordnet_pos else lemmatiser.lemmatize(word)
        lemmas_sent.append(lemma)
    # remove repeated tokens
    lemmas_sent = list(OrderedDict.fromkeys(lemmas_sent))
    # Rebuild text
    input_text = (" ").join(lemmas_sent)
    return input_text
