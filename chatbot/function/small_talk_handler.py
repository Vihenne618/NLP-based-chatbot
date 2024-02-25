from sklearn.feature_extraction.text import TfidfVectorizer
import sys
sys.path.append('..')
from chatbot.tool import calculate_similarity
from chatbot.tool import format_tool
from chatbot.tool import text_process

# Use similarity to match answers
def operation(chatbot, chatbot_model):
    corpus = chatbot_model.corpus
    word_vector = chatbot_model.word_vector
    vectorizer = chatbot_model.vectorizer
    input_text = chatbot.context.user_input

    # User input statement preprocessing
    input_text = text_process.preprocess_input(input_text)
    # Converts input statements to vectors
    vector = calculate_similarity.generate_text_vectors(input_text, vectorizer)
    # calculate the similarity
    max_similarity, max_similarity_index = calculate_similarity.get_max_similarity(vector, word_vector, vectorizer, chatbot_model.threshold)

    if max_similarity_index == None:
        format_tool.bot_response("I'm sorry, I don't understand that.")
        chatbot.context = None
        return None
    # query the answer
    answer = corpus["Answer"][max_similarity_index]
    format_tool.bot_response(answer)
    # Clear context
    chatbot.context = None

