import sys
sys.path.append('..')
from chatbot.tool import calculate_similarity
from chatbot.tool import text_process

# the chatbot intent list
intent_list = ["identity_management","small_talk","question_answer","transactions","exit"]

# The matching rule for program intent exits
exit_rules = ["exit","quit"]

def get_intents():
    # user intent in system
    return intent_list

# match user intent based similarity  
def martch_intent(chatbot, input_text):
    matched_intent = None
    # The most similar item in intent
    max_similarity = 0
    max_similarity_index = None

    # User input statement preprocessing
    input_text = text_process.preprocess_input(input_text)
    if input_text in exit_rules:
        matched_intent = "exit"
        return matched_intent

    intents = intent_list[:-1]
    for intent in intents:
        # get model vectors
        model = chatbot.models[intent]
        word_vectors = model.word_vector
        vectorizer = model.vectorizer

        # Converts input statements to vectors
        vector = calculate_similarity.generate_text_vectors(input_text, vectorizer)
        # calculate the similarity
        max_item_similarity, max_item_similarity_index = calculate_similarity.get_max_similarity(vector, word_vectors, vectorizer, model.threshold)
        # Remember the most similar intent terms
        if max_item_similarity > max_similarity:
            max_similarity = max_item_similarity
            max_similarity_index = max_item_similarity_index
            matched_intent = intent
    return matched_intent
