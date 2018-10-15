# https://raw.githubusercontent.com/wessilfie/BasicBGMBot/master/app.py
import random
from flask import Flask, request
from pymessenger.bot import Bot
import os
from web_scraper import get_restaurant_menu, get_restaurant_entree

RESTAURANT_ORDER = {"CAFE_3": 0,
                    "CLARK_KERR_CAMPUS": 1,
                    "CROSSROADS": 2,
                    "FOOTHILL": 3,
                    }

app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot (ACCESS_TOKEN)

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
              if message.get('message'):
                  #Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):
                        response_sent_text = get_message(message['message'].get('text'))
                        send_message(recipient_id, response_sent_text)
                    #if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        response_sent_nontext = get_message()
                        send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a random message to send to the user
def get_message(command):
    # Finds and executes the given command, filling in response
    default_response = "Not sure what you mean. Try *{}*.".format("crossroads lunch")
    response = None
    # This is where you start to implement more commands!
    command_parts = command.split(" ")
    print(command_parts)
    # if len(command_parts) == 1:
    #     restaurant = command_parts[0].upper()
    #     response = get_day_menu(restaurant)
    #     print(response)
    if len(command_parts) == 2:
        restaurant, meal = command_parts
        restaurant = command_parts[0].upper()
        meal = command_parts[1][0].upper() + command_parts[1][1:].lower()
        if restaurant in RESTAURANT_ORDER:
            response = get_restaurant_menu(restaurant, meal)
    elif len(command_parts) == 3:
        restaurant, meal, entree = command_parts
        restaurant = command_parts[0].upper()
        entree = entree.upper()
        meal = command_parts[1][0].upper() + command_parts[1][1:].lower()
        if restaurant in RESTAURANT_ORDER:
            response = get_restaurant_entree(restaurant, meal, entree)
    return response or default_response

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    app.run()
