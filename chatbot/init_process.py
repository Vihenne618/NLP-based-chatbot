from .tool import *
from .chatbot_model import ChatbotModel, Chatbot, ChatbotContent
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

# model data
model_data = {
    "identity_management" : "./chatbot/dataset/identity_management_dataset.csv",
    "small_talk" : "./chatbot/dataset/small_talk_dataset.csv",
    "question_answer" : "./chatbot/dataset/question_answer_dataset.csv",
    "transactions" : "./chatbot/dataset/transactions_dataset.csv"
}

# model path
model_paths = {
    "identity_management" : "./model_identity_management.pkl",
    "small_talk" : "./model_small_talk.pkl",
    "question_answer" : "./model_question_answer.pkl",
    "transactions" : "./model_transactions.pkl"
    }

# get the model by user intent
def get_model(intent):
    model_path = model_paths[intent]
    with open(model_path, mode='rb') as f:
        chatbot_model = pickle.load(f)
    return chatbot_model

# get model storage path
def get_model_path(intent):
    return model_paths[intent]

# init the chatbot
def init_chatbot():
    chatbot = Chatbot()
    chatbot_models = {}
    # load the chatbot model
    for key, value in model_data.items():
        # get the train model
        chatbot_model = get_model(key)
        chatbot_models[key] = chatbot_model
    chatbot.models = chatbot_models
    # load the Menu data
    chatbot.menu = load_data.load_menu()
    # load the Order data
    chatbot.client_orders = load_data.load_order()
    return chatbot

# init chatbot context
def init_chatbot_context(chatbot, user_intent, user_input):
    # get the crrent model
    chatbot_model = chatbot.models[user_intent]
    # Record context
    chatbot_content = ChatbotContent()
    chatbot_content.user_input = user_input
    chatbot_content.current_intent = user_intent
    chatbot_content.current_model = chatbot_model
    chatbot.context = chatbot_content

# train the model
def train_model():
    # load the dataset and train the model
    model_list = []
    t_vectorizer = TfidfVectorizer()
    corpus = []

    # load the data
    for key, value in model_data.items():
        data = load_data.load_data(value)
        process_data = text_process.process_text_list(data['Question'])
        corpus.extend(process_data)
        # init the chatbot model
        chatbot_model = ChatbotModel()
        chatbot_model.mode = key
        chatbot_model.corpus = data
        if key == 'small_talk':
            chatbot_model.threshold = 0.4
        model_list.append(chatbot_model)

    # fit the model by corpus
    t_vectorizer.fit(corpus)

    # train the model 
    for chatbot_model in model_list:
        chatbot_model.train(t_vectorizer)
        path = get_model_path(chatbot_model.mode)
        with open(path, mode='wb') as f:
            pickle.dump(chatbot_model, f)
    return None
