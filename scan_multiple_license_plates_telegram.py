from bs4 import BeautifulSoup
from requests import Request, Session, Timeout, ConnectionError
import re
import sys
import argparse
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import time
import pytz
from datetime import datetime
import glob
from random import randrange

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--combination', action='append', help='Multiple Parameter. Format is letter:number. Use ? for wildcard. Max length 2 letters and 3 numbers allowed.')
parser.add_argument('-t', '--timestamps', action='append', help='Multiple Parameter. Timestamps to query in 24h notation and in Berlin Time Zone. E.g. 12:00:00')
parser.add_argument('--telegram-bot-token', help='the token for the telegram bot')
parser.add_argument('--telegram-chat-id', help='the id of the telegram chat where to post the message')
args = parser.parse_args()

combinations = args.combination
timestamps = args.timestamps
token = args.telegram_bot_token
chatId = args.telegram_chat_id

if (not combinations or not timestamps or not token or not chatId):
    print('Mandatory parameters not set. See --help')
    sys.exit(1)


# Constants
lineDelimeter = '\n\n'
resultDelimeter = '|'
bot = telegram.Bot(token=token)
tz = pytz.timezone('Europe/Berlin')

# TODO make user agent random out of preconfigured set of user agents
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

def validNumbers(numbers):
    # TODO check for only numbers or wildcard
    if (len(numbers) > 3):
        return False
    return True

def validLetters(letters):
    # TODO check for only letters or wildcard
    if (len(letters) > 3):
        return False
    return True

def getPaginationMessage(soup):
    span = soup.select(".blaettern span")
    if (len(span) > 0):
        return span[0].get_text(strip=True)
    return None

def getCookiesAndTimestamp(session):
    getReq = Request(
        'GET', 
        'https://laikra.komm.one/dvvlaikraIGV21/servlet/Internetgeschaeftsvorfaelle?AUFRUF=WKZ_lhs'
    ).prepare()

    try:
        res=session.send(getReq, timeout=5)
        
        # Cookie from first Get Request we need for post request
        cookies = res.cookies.get_dict()

        # Also save timestamp from first request. It seams with a other timestamp server is rejecting post request
        soup = BeautifulSoup(res.text , 'html.parser')
        timestamp = soup.find('input', {'name': 'ZEITSTEMPEL'}).get('value')

        return cookies, timestamp, None
    except Timeout:
        errorMessage = f'\U000026D4 Error retrieving cookie. Timeout'
        return None, None, errorMessage
    except ConnectionError:
        errorMessage = f'\U000026D4 Error retrieving cookie. ConnectionError'
        return None, None, errorMessage

def getPlates(session, cookies, timestamp, letters, numbers):
    #print (f'search with {numbers}, {letters}, {timestamp}')
    
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

    try:
        postRes = session.send(postReq)

        soup = BeautifulSoup(postRes.text , 'html.parser')

        foundResults = soup.findAll('div', id=re.compile(r"^OPT_KENNZEICHENSUCHE_TREFFER\d+"))

        resultString = ''
        if (len(foundResults) == 0):
            resultString=f'\U0000274C Found {len(foundResults)} Results for S-{letters} {numbers}'
        else:
            resultString=f'\U00002705 Found {len(foundResults)} Results for S-{letters} {numbers}:\n'

            paginationMessage = getPaginationMessage(soup)
            if (paginationMessage != None):
                 resultString = resultString + f'\U000026A0 Warning. More Entries than shown: {paginationMessage}\n'

            sanitized = map(lambda entry: entry.get_text(strip=True), foundResults) 
            resultsJoined = resultDelimeter.join(sanitized)
            resultString = resultString + '\n' + resultsJoined
        # return timestamp needed for further requests
        timestamp = soup.find('input', {'name': 'ZEITSTEMPEL'}).get('value')
        return resultString, timestamp
    except Timeout:
        errorMessage = f'\U000026D4 Error retrieving License Plates for combination {letters}{numbers}. Timeout'
        return errorMessage, None
    except ConnectionError:
        errorMessage = f'\U000026D4 Error retrieving License Plates for combination {letters}{numbers}. ConnectionError'
        return errorMessage, None

def sendMessageToTelegram(message):
    bot.sendMessage(chat_id=chatId, text=message)

def sendImageToTelegram(path):
    photo=open(path, 'rb')
    bot.sendPhoto(chat_id=chatId, photo=photo, caption='Enjoy')

def scanCombinations(combinations):
    #print(f'Scanning combinations {combinations}')
    session = Session()
    cookies, timestamp, errorMessage = getCookiesAndTimestamp(session)

    if (errorMessage != None):
        return errorMessage

    if (cookies == None or timestamp == None):
        return "Could not get initial Cookie"

    results = {}
    for combination in combinations:
        #print(f'Processing {combination}')
        combination = combination.upper()
        letters, numbers = combination.split(':', 1)
       
        if (validNumbers(numbers) and validLetters(letters)):
            #print(f'Execute combinations {letters}-{numbers}')

            # TODO add some backoff here
            result, timestamp = getPlates(session, cookies, timestamp, letters, numbers)
            if (result != None and timestamp != None):
                results[combination] = result
        else:
            results[combination] = '\U000026D4 Invalid combination'
            #print(f'Skip invalid combination {combination}')

    resultsString = lineDelimeter.join([f'{key} -> {value}' for key, value in results.items()])
    return resultsString

def getCurrentBerlinTimestamp():
    berlin_now = datetime.now(tz)
    return berlin_now.strftime('%H:%M:%S')

def shouldFire():
    currentTime = getCurrentBerlinTimestamp()
    if currentTime in timestamps:
        return True
    return False

def loop(): 
    while(True):
        if (shouldFire()):
            results = scanCombinations(combinations)
            sendMessageToTelegram(results)
        time.sleep(1)

def scanAll(update: telegram.Update, context: CallbackContext) -> None:
    resultMessage = scanCombinations(combinations)
    update.message.reply_text(resultMessage)

def scan(update: telegram.Update, context: CallbackContext) -> None:
    entries = context.args
    if (entries != None and len(entries) > 0):
        resultMessage = scanCombinations(entries)
        update.message.reply_text(resultMessage)
    else:
        update.message.reply_text('\U000026D4 Please provide combination (<letters>:<numbers>)')

def getRandomImage():
    files=glob.glob("./images/*.jpg")
    entry = randrange(len(files))
    return files[entry]

def image(update: telegram.Update, context: CallbackContext) -> None:
    path = getRandomImage()
    sendImageToTelegram(path)

def help_command(update: telegram.Update, context: CallbackContext) -> None:
    update.message.reply_text('\U000026A0 Usage: \U000026A0\n /scanAll to trigger a run of the configured license plates\n /scan <Combination> to trigger a search of the given combination\n /butterfly: to show some nice stuff')

if __name__ == '__main__':
    print(f'Service will query combinations {combinations} at following times {timestamps} in Timezone {tz}')
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("scanAll", scanAll))
    dispatcher.add_handler(CommandHandler("scan", scan))
    dispatcher.add_handler(CommandHandler("butterfly", image))
    dispatcher.add_handler(CommandHandler("help", help_command))
    updater.start_polling()
    try:
        loop()
    except KeyboardInterrupt:
        print(sys.stderr, 'Exit by User')
        updater.idle()
        sys.exit(0)