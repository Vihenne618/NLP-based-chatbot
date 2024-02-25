from .function import intent_matching, identity_management_handler, small_talk_handler, question_answer_handler, transactions_handler, exit_handler
from .tool import *
from sklearn.feature_extraction.text import TfidfVectorizer

# chat model class
class ChatbotModel():

    def __init__(self):
        # chatbot mode: 1.identity_management, 2.small_talk, 3.question_answer, 4.transactions
        self.mode = None
        # corpora in the current mode 
        self.corpus = []
        # word vectors for all sentences in the current corpus
        self.word_vector = None
        # vectorizer
        self.vectorizer = None
        # similarity threshold
        self.threshold = 0.2
        
    def train(self, vectorizer = TfidfVectorizer()):
        self.vectorizer = vectorizer
        # Generated word vector
        if len(self.corpus) != 0:
            word_vector = text_process.process_text_list(self.corpus['Question'])
            word_vector = self.vectorizer.transform(word_vector)
            self.word_vector = word_vector
        return None
    
    def answer(self, chatbot): 
        # Get chatbot context
        intent = chatbot.context.current_intent
        while chatbot.context != None:
            intent_list = intent_matching.get_intents()
            # enters different processing depending on the user's intent
            if intent == intent_list[0]:
                identity_management_handler.operation(chatbot, self)
            elif intent == intent_list[1]:
                small_talk_handler.operation(chatbot, self)
            elif intent == intent_list[2]:
                question_answer_handler.operation(chatbot, self)
            elif intent == intent_list[3]:
                transactions_handler.operation(chatbot, self)
            else:
                format_tool.bot_response("I'm sorry, I don't understand that.")
        return None
    
# chatbot content class
class ChatbotContent():
    def __init__(self):
        self.user_input = None
        self.current_intent = None
        self.current_backlog  = None
        self.backlogs = []
        self.current_model = None

# chatbot class
class Chatbot():
    def __init__(self):
        # Chatbot model list
        self.models = {}
        # Chatbot Context information
        self.context = ChatbotContent()
        
        # Session data
        self.session_data = {}
        # transactions data
        self.menu = []
        self.client_orders = {}

    def answer(self): 
        if self.context == None:
            return None
        #load current chatbot_model
        chatbot_model = self.context.current_model
        if chatbot_model == None or self.context.user_input == None:
            return None
        # run the model to 
        chatbot_model.answer(chatbot=self)

# dish in menu
class Dish():
    def __init__(self):
        self.dish_name = None
        self.price = 0
        self.quantity = 0

# Customer order
class Order():
    def __init__(self):
        self.user_name = None
        self.tel = None
        self.time = None
        self.diners_quantity = None
        self.dishes = []
        self.order_amount = 0
        self.remark = None
        # order_status: unpaid,complete
        self.order_status = None
