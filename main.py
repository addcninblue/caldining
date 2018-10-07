import os
import time
import re
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from slackclient import SlackClient


# https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
RESTAURANT_ORDER = {"CAFE_3": 0,
                    "CLARK_KERR_CAMPUS": 1,
                    "CROSSROADS": 2,
                    "FOOTHILL": 3,
                    }

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format("crossroads lunch")

    # Finds and executes the given command, filling in response
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

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

# https://realpython.com/python-web-scraping-practical-introduction/
def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)

def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def get_restaurant_data(restaurant_name):
    raw_html = simple_get('https://caldining.berkeley.edu/menu.php')
    html = BeautifulSoup(raw_html, 'html.parser')
    restaurants = html.findAll("div", class_="menu_wrap_overall")
    return restaurants[RESTAURANT_ORDER[restaurant_name]]

# get_croads_menu()

def parse_restaurant_data(data):
    menu = {}
    for meal in data:
        meal_menu = {}
        try:
            meal_name = meal.select("h3.location_period")[0].text[1:]
            current_type = None
            for p in meal.select("p"):
                # print(p)
                new_class = p.attrs.get('class')
                if new_class:
                    current_type = p.text[1:]
                    meal_menu[current_type] = []
                else:
                    meal_menu[current_type].append(p.text[1:-1])

            menu[meal_name] = meal_menu
        except:
            pass
    return menu

def format_data_meal(data):
    output = ""
    for item in data:
        output += f'*{item}*\n'
        for food in data[item]:
            output += f'{food}\n'
    return output

def get_restaurant_menu(restaurant, meal):
    data = get_restaurant_data(restaurant)
    parsed = parse_restaurant_data(data)
    meal_data = parsed.get(meal)
    if meal_data:
        return format_data_meal(meal_data)
    else:
        return None

def get_day_menu(restaurant):
    data = get_restaurant_data(restaurant)
    parsed = parse_restaurant_data(data)
    formatted = format_data_meal(parsed)
    return formatted

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
