from bs4 import BeautifulSoup
from requests import Request, Session
import re
import sys
import argparse
import telegram
import time

timeout = 60 * 60 * 4

parser = argparse.ArgumentParser()
parser.add_argument('--letters', help='letter combination. Use ? for wildcard. Max length 2 letters')
parser.add_argument('--numbers', help='number combination. Use ? for wildcard. Max length 3 digits')
parser.add_argument('--telegram-bot-token', help='the token for the telegram bot')
parser.add_argument('--telegram-chat-id', help='the id of the telegram chat where to post the message')
args = parser.parse_args()

numbers = args.numbers
letters = args.letters.upper()
token = args.telegram_bot_token
chatId = args.telegram_chat_id

if (not numbers or not letters or not token or not chatId):
    print('Mandatory parameters not set. See --help')
    sys.exit(1)

if (len(numbers) > 3):
    print('Only 3 Digits as numbers allowed')
    sys.exit(1)

if (len(letters) > 3):
    print('Only 2 letters as letters allowed')
    sys.exit(1)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Origin': 'https://laikra.komm.one',
    'Connection': 'keep-alive',
    'Referer': 'https://laikra.komm.one/dvvlaikraIGV21/servlet/Internetgeschaeftsvorfaelle?AUFRUF=WKZ_lhs',
    'Upgrade-Insecure-Requests': '1',
    'TE': 'Trailers'
}

def getPlates():
    s = Session()

    getReq = Request(
        'GET', 
        'https://laikra.komm.one/dvvlaikraIGV21/servlet/Internetgeschaeftsvorfaelle?AUFRUF=WKZ_lhs'
    ).prepare()

    getResponse=s.send(getReq)
    # Cookie from first Get Request we need for post request
    cookies=getResponse.cookies.get_dict()

    # Also save timestamp from first request. It seams with a other timestamp server is rejecting post request
    soup = BeautifulSoup(getResponse.text , 'html.parser')
    timestamp = soup.find('input', {'name': 'ZEITSTEMPEL'}).get('value')

    data = {
        "WKZ_ERKENN_Z": letters,
        "WKZ_ZIFFERN": numbers,
        "WKZ_SUCHMERKMAL": "NULL",
        "BTN_WKZSUCHE": "suchen",
        "ZEITSTEMPEL": timestamp
    }

    postReq = Request(
        'POST', 
        'https://laikra.komm.one/dvvlaikraIGV21/servlet/Internetgeschaeftsvorfaelle',
        files= {
            'WKZ_ERKENN_Z': (None, data['WKZ_ERKENN_Z']),
            'WKZ_ZIFFERN': (None, data['WKZ_ZIFFERN']),
            'WKZ_SUCHMERKMAL': (None, data['WKZ_SUCHMERKMAL']),
            'ZEITSTEMPEL': (None, data['ZEITSTEMPEL']),
            'BTN_WKZSUCHE': (None, data['BTN_WKZSUCHE'])
        },
        cookies = cookies,
        headers = headers
    ).prepare()

    postRes = s.send(postReq)

    soup = BeautifulSoup(postRes.text , 'html.parser')

    # check if 'blaettern' exists, which indicates, more results available than shown - todo
    pagination = False
    paginationMessage = ''
    span = soup.select(".blaettern span")
    if (len(span) > 0):
        pagination = True
        paginationMessage = span[0].get_text(strip=True)

    selected = soup.findAll('div', id=re.compile(r"^OPT_KENNZEICHENSUCHE_TREFFER\d+"))

    result=f'Found {len(selected)} Results for S-{letters} {numbers}:\n'

    if (pagination):
        result = result + f'Warning. More Entries than shown: {paginationMessage}\n'

    if (len(selected) > 0):
        for entry in selected:
            result = result + (entry.get_text(strip=True)) + ' | '
    #else:
    #    result = result + 'No Results available'

    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chatId, text=result)

while(True):
    getPlates()
    time.sleep(timeout)