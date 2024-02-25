import sys
sys.path.append('..')
from chatbot.tool import format_tool
from chatbot.tool import text_process
from chatbot.tool import calculate_similarity
from chatbot.function.identity_management_handler import extract_name_from_sentences
from chatbot.chatbot_model import Order, Dish
from chatbot.tool import load_data
import re

# Business intent
transactions_intents = ["BOOKING","ORDER","CANCEL","CHECK_ORDER","SETTLE","SHOW_MENU","CHECK_BOOKING","MODIFY_BOOKING"]
intent_backlog = {
    "BOOKING": ["ask_name","booking"],
    "CHECK_BOOKING": ["ask_name","show_booking"],
    "MODIFY_BOOKING": ["ask_name","modify_booking"],

    "ORDER": ["ask_name","show_menu","order_dish"],
    "CANCEL": ["ask_name","show_order","cancel_order"],
    "CHECK_ORDER": ["ask_name","show_order"],

    "SETTLE": ["ask_name","show_order","settle_order"],
    "SHOW_MENU": ["show_menu"]
}

def operation(chatbot, chatbot_model):
    backlogs = chatbot.context.backlogs
    if(backlogs is not None and len(backlogs) > 0):
        chatbot.context.current_backlog = chatbot.context.backlogs[-1]
        current_backlog = chatbot.context.current_backlog
        # operation result: succeed, fail, cancel, next
        result = "succeed"
        if current_backlog == "ask_name":
            result = ask_name(chatbot)
        elif current_backlog == "booking":
            result = booking(chatbot)
        elif current_backlog == "show_menu":
            result = show_menu(chatbot)
        elif current_backlog == "order_dish":
            result = order_dish(chatbot)
        elif current_backlog == "show_order":
            result = show_order(chatbot)
        elif current_backlog == "settle_order":
            result = settle_order(chatbot)
        elif current_backlog == "show_booking":
            result = show_booking(chatbot)
        elif current_backlog == "modify_booking":
            result = modify_booking(chatbot)
        else:
            result = cancel_order(chatbot)

        # Result processing
        if result == "cancel":
            # Clear context
            chatbot.context = None
            return None
        elif result == "fail":
            # try again
            return None
        elif result == 'next':
            # go to next step
            return None
        else:
            if len(backlogs) == 1:
                chatbot.context = None
                return None
            elif len(backlogs) > 1:
                # remove the last element
                chatbot.context.backlogs.pop()
                return None
            else:
                return None

    # get question intent
    question_intent = get_question_intent(chatbot, chatbot_model)
    if question_intent is None: 
        format_tool.bot_response("I'm sorry, I don't understand that.")
        chatbot.context = None
        return None

    # Convert question intent to backlogs
    chatbot.context.backlogs = []
    chatbot.context.backlogs.extend(intent_backlog.get(question_intent,[]))
    chatbot.context.backlogs.reverse()
    return None

    
# check User Name
def ask_name(chatbot):
    user_name = chatbot.session_data.get("user_name",None)
    if(user_name is not None and user_name != ""):
        return "succeed"
    format_tool.bot_response("Hello, Could you please tell me your name?")
    for i in range(3):
        name_input = format_tool.user_input()
        user_name = extract_name_from_sentences(name_input)
        if user_name is None or user_name == "":
            if i == 2:
                format_tool.bot_response("I'm sorry, I don't understand that.")
            else:
                format_tool.bot_response("Sorry, I didn't recognise your name, can you say again?")
            continue
        else:
            chatbot.session_data["user_name"] = user_name
            return "succeed"
    return "cancel"
        
    

# list Menu content
def show_menu(chatbot):
    menu_data = chatbot.menu
    if menu_data is None:
        return "cancel"
    show_data = "The restaurant's menu is listed below:\n"
    dish_names = menu_data["Dish_name"]
    prices = menu_data["Price"]
    show_data += "    "
    show_data += "Dish Name".ljust(30)
    show_data += "Price\n"
    for i, value in enumerate(menu_data["ID"]):
        show_data += "    "
        show_data += dish_names[i].ljust(30)
        show_data += str(prices[i])
        show_data += "\n"
    format_tool.bot_response(show_data)
    return "succeed"

# show booking
def show_booking(chatbot):
    user_name = chatbot.session_data.get("user_name",None)
    if user_name is None or user_name == "":
        format_tool.bot_response("Sorry, user information is incorrect.")
        return "cancel"
    user_order = chatbot.client_orders.get(user_name, None)
    if user_order is None:
        format_tool.bot_response("Sorry, you currently have no booking.")
        return "cancel"
    # print the order detail
    print_booking_detail(user_order)
     # Ask the user if they want to check out now
    if user_order.order_status == "unpaid":
        format_tool.bot_response("Do you need to change your booking?(Yes/No)")
        user_input = format_tool.user_input()
        if user_input is not None and user_input.lower() == "yes":
            chatbot.context.backlogs = []
            chatbot.context.backlogs.extend(intent_backlog.get(transactions_intents[7],[]))
            chatbot.context.backlogs.reverse()
            return "next"
        else:
            format_tool.bot_response("All right.")
    return "succeed"

# print the order detail
def print_booking_detail(user_order):
    response_data = "Dear " + user_order.user_name + ", your booking is as follows:\n"
    response_data += "  Customer Name: " + user_order.user_name + "\n"
    if user_order.tel is not None:
        response_data += "  Tel: " + str(user_order.tel) + "\n"
    if user_order.time is not None:
        response_data += "  Time of booking: " + user_order.time + "\n"
    if user_order.diners_quantity is not None:
        response_data += "  Number of diners: " + str(user_order.diners_quantity) + "\n"
    if user_order.remark is not None:
        response_data += "  Remark: " + user_order.remark + "\n"
    if user_order.dishes is not None and len(user_order.dishes) > 0 :
        response_data += "    Dish Name".ljust(30)
        response_data += "Price($)".ljust(10)
        response_data += "Quantity\n"
        for dish in user_order.dishes:
            response_data += "    "
            response_data += dish.dish_name.ljust(30)
            response_data += str(dish.price).ljust(10)
            response_data += str(dish.quantity)
            response_data += "\n"
        response_data += "  Total amount of bill: " + str("{:.3f}".format(user_order.order_amount)) + ".\n"
    format_tool.bot_response(response_data)

# show the order content
def show_order(chatbot):
    user_name = chatbot.session_data.get("user_name",None)
    if user_name is None or user_name == "":
        format_tool.bot_response("Sorry, user information is incorrect.")
        return "cancel"
    user_order = chatbot.client_orders.get(user_name, None)
    if user_order is None:
        format_tool.bot_response("Sorry, you currently have no orders.")
        return "cancel"
    response_data = "Dear " + user_order.user_name + ", your order is as follows:\n"
    response_data += "  Customer Name: " + user_order.user_name + "\n"
    if user_order.tel is not None:
        response_data += "  Tel: " + str(user_order.tel) + "\n"
    if user_order.time is not None:
        response_data += "  Time of booking: " + user_order.time + "\n"
    if user_order.diners_quantity is not None:
        response_data += "  Number of diners: " + str(user_order.diners_quantity) + "\n"
    if user_order.remark is not None:
        response_data += "  Remark: " + user_order.remark + "\n"
    if user_order.dishes is not None and len(user_order.dishes) > 0 :
        response_data += "    Dish Name".ljust(30)
        response_data += "Price($)".ljust(10)
        response_data += "Quantity\n"
        for dish in user_order.dishes:
            response_data += "    "
            response_data += dish.dish_name.ljust(30)
            response_data += str(dish.price).ljust(10)
            response_data += str(dish.quantity)
            response_data += "\n"
        response_data += "  Total amount of bill: " + str("{:.3f}".format(user_order.order_amount)) + ".\n"
    format_tool.bot_response(response_data)
    return "succeed"

# booking operation
def booking(chatbot):
    user_name = chatbot.session_data.get("user_name",None)
    if user_name is None or user_name == "":
        format_tool.bot_response("Sorry, user information is incorrect.")
        return "cancel"
    new_order = Order()
    new_order.user_name = user_name
    new_order.order_status = "unpaid"
    old_order = chatbot.client_orders.get(user_name, None)
    if old_order is not None:
        new_order.tel = old_order.tel
    chatbot.client_orders[user_name] = new_order

    # ask phone
    order = chatbot.client_orders.get(user_name, None)
    phone = order.tel
    if(phone is None):
        format_tool.bot_response("Can I have your contact number?")
        phone = format_tool.user_input()
        re.findall(r'\d+', phone)
        if phone is None:
            format_tool.bot_response("I'm sorry, I don't understand. Can you repeat again?")
            return "fail"
        chatbot.client_orders[user_name].tel = phone
    
    # ask time
    order = chatbot.client_orders.get(user_name, None)
    time = order.time
    if(time is None):
        format_tool.bot_response("What time would you like to book to dine?")
        time = format_tool.user_input()
        if time is None:
            format_tool.bot_response("I'm sorry, I don't understand. Can you repeat again?")
            return "fail"
        chatbot.client_orders[user_name].time = time
    
    # ask diners quantity
    order = chatbot.client_orders.get(user_name, None)
    diners_quantity = order.diners_quantity
    if(diners_quantity is None):
        format_tool.bot_response("How many people dined?")
        diners_quantity = format_tool.user_input()
        match = re.search(r'\d+',diners_quantity)
        diners_quantity = match.group() if match else None
        if diners_quantity is None:
            format_tool.bot_response("I'm sorry, I don't understand. Can you repeat again?")
            return "fail"
        chatbot.client_orders[user_name].diners_quantity = diners_quantity

    # ask remark
    order = chatbot.client_orders.get(user_name, None)
    remark = order.remark
    if(remark is None):
        format_tool.bot_response("Do you have any special requirements or preferences that need to be noted?")
        remark = format_tool.user_input()
        if remark is not None:
            chatbot.client_orders[user_name].remark = remark

    # booking succeed
    format_tool.bot_response("You have successfully booked! Thank you for your patronage.")
    load_data.save_order(chatbot.client_orders)
    # print the order detail
    print_booking_detail(chatbot.client_orders[user_name])

    # Ask if want to order food 
    chatbot.client_orders[user_name].dishes = None
    format_tool.bot_response("Do you need to order some food now?(Yes/No)")
    user_input = format_tool.user_input()
    if user_input is not None and user_input.lower() == "yes":
        chatbot.context.backlogs = []
        chatbot.context.backlogs.extend(intent_backlog.get(transactions_intents[1],[]))
        chatbot.context.backlogs.reverse()
        return "next"
    else:
        format_tool.bot_response("All right.")
        return "succeed"
    return "succeed"

# modify booking operation
def modify_booking(chatbot):
    user_name = chatbot.session_data.get("user_name",None)
    if user_name is None or user_name == "":
        format_tool.bot_response("Sorry, user information is incorrect.")
        return "cancel"
    user_order = chatbot.client_orders.get(user_name, None)
    if user_order is None:
        format_tool.bot_response("Sorry, you currently have no booking.")
        return "cancel"
    # print the booking detail
    print_booking_detail(chatbot.client_orders[user_name])
    # Confirmation of the need to modify the order
    format_tool.bot_response("Are you sure change your booking?(Yes/No)")
    user_input = format_tool.user_input()
    if user_input is not None and user_input.lower() == "yes":
        user_order.time = None
        user_order.diners_quantity = None
        user_order.dishes = None
        user_order.order_amount = None
        user_order.remark = None
        chatbot.client_orders[user_name] = user_order
        chatbot.context.backlogs = []
        chatbot.context.backlogs.extend(intent_backlog.get(transactions_intents[0],[]))
        chatbot.context.backlogs.reverse()
        return "next"
    else:
        format_tool.bot_response("All right.")
    return "succeed"
    
# order dish
def order_dish(chatbot):
    user_name = chatbot.session_data.get("user_name",None)
    if user_name is None or user_name == "":
        format_tool.bot_response("Sorry, user information is incorrect.")
        return "cancel"

    user_order = chatbot.client_orders.get(user_name, None)
    if user_order is None:
        user_order = Order()
        user_order.user_name = user_name
        user_order.order_status = "unpaid"
        chatbot.client_orders[user_name] = user_order
    
    format_tool.bot_response("Which dishes do you want to choose?")
    format_tool.bot_response("If you're done ordering, you can type 'finish'.")
    menu = chatbot.menu
    user_order.dishes = []
    while True:
        user_input = format_tool.user_input()
        if user_input == "finish":
            break
        select_dish, quantity = user_select_dish(user_input)
        if select_dish is None or quantity is None:
            format_tool.bot_response("Sorry, please specify the name and quantity of the dish you have chosen.")
            continue
        dish_name,price = get_menu_item(menu, select_dish)
        if dish_name is not None:
            dish = Dish()
            dish.dish_name = dish_name
            dish.price = price
            dish.quantity = quantity
            user_order.dishes.append(dish)
            format_tool.bot_response("Add Success.")
        else:
            format_tool.bot_response("Sorry, please specify the name and quantity of the dish you have chosen.")
    if len(user_order.dishes) == 0:
        format_tool.bot_response("Order failed, you did not select any dishes.")
        return "cancel"
    format_tool.bot_response("Order successful, thank you!")
    totle_amount = 0
    for dish in user_order.dishes:
        totle_amount += float(dish.price) * float(quantity)
    user_order.order_amount = totle_amount
    # save order data
    chatbot.client_orders[user_name] = user_order
    load_data.save_order(chatbot.client_orders)
    # show order detail
    chatbot.context.backlogs = []
    chatbot.context.backlogs.extend(intent_backlog.get(transactions_intents[3],[]))
    chatbot.context.backlogs.reverse()
    return "next"

def get_menu_item(menu = [], select_dish = None):
    if select_dish is None:
        return None, None
    dish_names = menu["Dish_name"]
    prices = menu["Price"]
    for i, menu_item in enumerate(menu["ID"]):
        dish_name = dish_names[i]
        price = prices[i]
        equit_dish_name = re.sub(r'[\d\s]', '', dish_name)
        if(equit_dish_name == select_dish):
            return dish_name,price
    return None, None

def user_select_dish(user_input):
    if user_input is None or user_input == '':
        return None, None
    match = re.search(r'\d+', user_input)
    quantity = match.group() if match else None
    dish_name = re.sub(r'[\d\s]', '', user_input)
    return dish_name, quantity
    
# settle order operation
def settle_order(chatbot):
    user_name = chatbot.session_data.get("user_name",None)
    if user_name is None or user_name == "":
        format_tool.bot_response("Sorry, user information is incorrect.")
        return "cancel"
    user_order = chatbot.client_orders.get(user_name, None)
    if user_order is None:
        format_tool.bot_response("Sorry, you currently have no booking.")
        return "cancel"
    
    # check order status
    if user_order.order_status != "unpaid":
        format_tool.bot_response("Your order has been paid for. Thank you.")
        return "succeed"
    # ask pay right now
    format_tool.bot_response("Do you want to check out now?(Yes/No)")
    user_input = format_tool.user_input()
    if user_input is None or user_input.lower() != "yes":
        format_tool.bot_response("All right.")
        return "succeed"
    # pay operation
    format_tool.bot_response("Would you like to pay by cash or card?")
    user_input = format_tool.user_input()
    # pay succeed
    user_order.order_status = "complete"
    chatbot.client_orders[user_name] = user_order
    load_data.save_order(chatbot.client_orders)
    format_tool.bot_response("Dear " + user_name + ", your bill totals £" + str("{:.3f}".format(user_order.order_amount)) + ".")
    format_tool.bot_response("Payment was successful. Welcome to dine with us again!")
    return "succeed"
    
# cancel the user order
def cancel_order(chatbot):
    user_name = chatbot.session_data.get("user_name",None)
    if user_name is None or user_name == "":
        format_tool.bot_response("Sorry, user information is incorrect.")
        return "cancel"
    user_order = chatbot.client_orders.get(user_name, None)
    if user_order is None:
        format_tool.bot_response("Sorry, you currently have no booking.")
        return "cancel"
    else:
        if user_order.order_status == "complete":
            format_tool.bot_response("Your order is complete and cannot be cancelled.")
            return "cancel"
    # cancel the booking
    format_tool.bot_response("Are you sure cancel your booking?(Yes/No)")
    user_input = format_tool.user_input()
    if user_input is None or user_input.lower() != "yes":
        format_tool.bot_response("All right.")
        return "succeed"
    # remove the order
    del chatbot.client_orders[user_name]
    load_data.save_order(chatbot.client_orders)
    format_tool.bot_response("The booking has been cancelled, thank you!")
    return "succeed"

# match the question and get the question intent
def get_question_intent(chatbot, chatbot_model):
    if chatbot.context is None:
        return None
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

    if max_similarity_index is None:
        return None
    
    # query the answer
    opera_intent = corpus["Intent"][max_similarity_index]
    return opera_intent