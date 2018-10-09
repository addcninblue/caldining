from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

RESTAURANT_ORDER = {"CAFE_3": 0,
                    "CLARK_KERR_CAMPUS": 1,
                    "CROSSROADS": 2,
                    "FOOTHILL": 3,
                    }


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
