from bs4 import BeautifulSoup
from requests import Request, Session
import re

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
    "WKZ_ERKENN_Z": "GO",
    "WKZ_ZIFFERN": "9??",
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

# Print for debug reasons
#print(postReq.headers)
#print(postReq.body.decode('utf-8'))

# send post request using mitm
postRes = s.send(postReq)

soup = BeautifulSoup(postRes.text , 'html.parser')
title = soup.find('title')
print(title)

print(r"""
      /\ \__         /\ \__/\ \__                        /\ \__   
  ____\ \ ,_\  __  __\ \ ,_\ \ ,_\    __      __     _ __\ \ ,_\  
 /',__\\ \ \/ /\ \/\ \\ \ \/\ \ \/  /'_ `\  /'__`\  /\`'__\ \ \/  
/\__, `\\ \ \_\ \ \_\ \\ \ \_\ \ \_/\ \L\ \/\ \L\.\_\ \ \/ \ \ \_ 
\/\____/ \ \__\\ \____/ \ \__\\ \__\ \____ \ \__/.\_\\ \_\  \ \__\
 \/___/   \/__/ \/___/   \/__/ \/__/\/___L\ \/__/\/_/ \/_/   \/__/
                                      /\____/                     
                                      \_/__/                      
 ___                                                          ___             __             
/\_ \    __                                                  /\_ \           /\ \__          
\//\ \  /\_\    ___     __    ___     ____     __       _____\//\ \      __  \ \ ,_\    __   
  \ \ \ \/\ \  /'___\ /'__`\/' _ `\  /',__\  /'__`\    /\ '__`\\ \ \   /'__`\ \ \ \/  /'__`\ 
   \_\ \_\ \ \/\ \__//\  __//\ \/\ \/\__, `\/\  __/    \ \ \L\ \\_\ \_/\ \L\.\_\ \ \_/\  __/ 
   /\____\\ \_\ \____\ \____\ \_\ \_\/\____/\ \____\    \ \ ,__//\____\ \__/.\_\\ \__\ \____\
   \/____/ \/_/\/____/\/____/\/_/\/_/\/___/  \/____/     \ \ \/ \/____/\/__/\/_/ \/__/\/____/
                                                          \ \_\                              
                                                           \/_/                              
                                                      
                                                      
  ____    ___     __      ___     ___      __   _ __  
 /',__\  /'___\ /'__`\  /' _ `\ /' _ `\  /'__`\/\`'__\
/\__, `\/\ \__//\ \L\.\_/\ \/\ \/\ \/\ \/\  __/\ \ \/ 
\/\____/\ \____\ \__/.\_\ \_\ \_\ \_\ \_\ \____\\ \_\ 
 \/___/  \/____/\/__/\/_/\/_/\/_/\/_/\/_/\/____/ \/_/    
""")

# check if 'blaettern' exists, which indicates, more results available than shown - todo
span = soup.select(".blaettern span")
if (len(span) > 0):
    print()
    print('WARNING: There are more Results than shown. Pagination is not supported yet')
    print(f'    ---> {span[0].get_text(strip=True)}')
    print()

selected = soup.findAll('div', id=re.compile(r"^OPT_KENNZEICHENSUCHE_TREFFER\d+"))

print(f'Found {len(selected)} Results:')
print('-------------------------------------------------------------------')

# Check amount of found Results
if (len(selected) > 0):
    for entry in selected:
        print(entry.get_text(strip=True))
else:
    print("No Results available")

print('==================================================================')