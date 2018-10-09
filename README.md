# Cal Dining Bot

This is a Slack + FB Messenger bot that sends the cal restaurant menu!

## Usage:

```
@diningapp crossroads lunch
@diningapp cafe_3 breakfast
```

## Installation:

```bash
git clone https://github.com/addcninblue/caldining
# create virtualenv
pip3 install -r requirements.txt
```

## Running:

Slack:
```bash
python3 main.py
```

FB Messenger:
```bash
gunicorn app:app
```
