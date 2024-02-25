from chatbot.function import intent_matching
from chatbot.function import exit_handler
from chatbot.tool import format_tool
from chatbot import init_process

# train the model
# init_process.train_model()

# init the Chatbot
chatbot = init_process.init_chatbot()

format_tool.bot_response('Hello! What can I help you?')
while True:
    # user input
    input_text = format_tool.user_input()
    
    # match user intent  
    user_intent = intent_matching.martch_intent(chatbot, input_text)

    # user exit, chat stop
    if user_intent == 'exit':
        exit_handler.operation(input_text)
        break
    elif user_intent == None:
        format_tool.bot_response("I'm sorry, I don't understand that.")
    else:
        # init the chatbot context
        init_process.init_chatbot_context(chatbot, user_intent, input_text)
        # answer user questions 
        chatbot.answer()






    

    