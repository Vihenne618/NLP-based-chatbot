from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Use TF-IDF to generate text feature vectors
def generate_text_vectors(input_text = "", vectorizer = TfidfVectorizer()):
    vectors = vectorizer.transform([input_text])
    return vectors

# Use TF-IDF to generate corpus feature vectors
def generate_corpus_vectors(corpus = [], vectorizer = TfidfVectorizer()):
    vectors = None
    if corpus :
        vectors = vectorizer.transform(corpus)
    return vectors

# calculate the vectors similarity, get return the max one
def get_max_similarity(vector = [], vectors = [], vectorizer = TfidfVectorizer(), threshold = 0):
    max_similarity = 0
    max_similarity_index = None
    if(vector == None or vectors == None or vector.getnnz() == 0 or vectors.getnnz() == 0):
        return max_similarity, max_similarity_index
    similarities = cosine_similarity(vector, vectors)
    max_similarity_index = similarities.argmax()
    max_similarity = similarities[0][max_similarity_index]
    if(max_similarity < threshold):
        max_similarity = 0
        max_similarity_index = None
    return max_similarity, max_similarity_index
    