from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk import pos_tag, ne_chunk
from nltk.tokenize import word_tokenize
import sys
sys.path.append('..')
from chatbot.tool import calculate_similarity
from chatbot.tool import format_tool
from chatbot.tool import text_process


# nltk.download('punkt')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')

# Use similarity to match answers
def operation(chatbot, chatbot_model):
    corpus = chatbot_model.corpus
    word_vector = chatbot_model.word_vector
    vectorizer = chatbot_model.vectorizer
    input_text = chatbot.context.user_input

    # Name ask process
    if chatbot.context.current_backlog == "ask_name":
        format_tool.bot_response("Sorry, Could you please tell me your name?")
        name_input = format_tool.user_input()
        user_name = extract_name_from_sentences(name_input)
        if user_name == None:
            format_tool.bot_response("I'm sorry, I don't understand that.")
            chatbot.context = None
            return None
        store_name_data(chatbot, user_name) 

    # User input statement preprocessing
    input_text_processed = text_process.preprocess_input(input_text)
    # Converts input statements to vectors
    vector = calculate_similarity.generate_text_vectors(input_text_processed, vectorizer)
    # calculate the similarity
    max_similarity, max_similarity_index = calculate_similarity.get_max_similarity(vector, word_vector, vectorizer, chatbot_model.threshold)
    if max_similarity_index == None:
        format_tool.bot_response("I'm sorry, I don't understand that.")
        chatbot.context = None
        return None

    # query user name
    user_name = query_user_name(chatbot, input_text, max_similarity_index, corpus)
    # generate the answer
    answer = generate_answer(chatbot, user_name, max_similarity_index, corpus)
    return None



# generate the answer
def generate_answer(chatbot, user_name, max_similarity_index, corpus = []):
    # query the answer
    answer = corpus["Answer"][max_similarity_index]
    question = corpus["Question"][max_similarity_index]
    # Generated answer
    if "{name}" in answer :
        if user_name != None :
            answer = answer.format(name = user_name)
        else:
            answer = "I'm sorry, I don't understand that."
    if "{name}" not in question and user_name == None:
        chatbot.context.current_intent = 'identity_management'
        chatbot.context.current_backlog = 'ask_name'
        return None
    format_tool.bot_response(answer)
    # Clear context
    chatbot.context = None
    return answer



# query user name
def query_user_name(chatbot, input_text, max_similarity_index, corpus = []):
    question = corpus["Question"][max_similarity_index]
    user_name = None
    # need save user name
    if "{name}" in question:
        # Extract names from sentences
        user_name = extract_name_from_sentences(input_text)
        # save user name 
        store_name_data(chatbot, user_name)
    # not need to save the user name    
    else:
        user_name = query_name_data(chatbot)
    return user_name



def store_name_data(chatbot, name):
    if name == None or name == '':
       return None  
    # with open("./user_info.txt", mode='wb') as f:
    #     pickle.dump(name, f)
    chatbot.session_data["user_name"] = name
    return name



def query_name_data(chatbot):
    name = None
    try:
        # with open("./user_info.txt", mode='rb') as f:
        #     name = pickle.load(f)
        name = chatbot.session_data.get("user_name",None)
    except Exception as e:
            name = None
    return name



# Extract names from sentences
def extract_name_from_sentences(input_text):
    words = word_tokenize(input_text)
    pos_tags = pos_tag(words)
    named_entities = ne_chunk(pos_tags)
    # get names
    names = []
    for entity in named_entities:
        if isinstance(entity, nltk.Tree) and entity.label() == 'PERSON':
            name = ' '.join([word for word, tag in entity.leaves()])
            names.append(name)
    name_str = None
    if len(names) != 0:
        name_str = names[0] 
    else:
        return None
    return name_str

