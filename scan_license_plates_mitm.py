from bs4 import BeautifulSoup
from requests import Request, Session
import re

# use mitm proxy
http_proxy  = "127.0.0.1:8080"
https_proxy = "127.0.0.1:8080"

proxyDict = { 
              "http"  : http_proxy, 
              "https" : https_proxy
            }

# needed header files
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'accept-language': 'de,en-US;q=0.7,en;q=0.3',
    'accept-encoding': 'gzip, deflate, br',
    'origin': 'https://laikra.komm.one',
    'content-Type': 'multipart/form-data; boundary=---------------------------21656587021738608004592965003',
    'connection': 'keep-alive',
    'referer': 'https://laikra.komm.one/dvvlaikraIGV21/servlet/Internetgeschaeftsvorfaelle?AUFRUF=WKZ_lhs',
    'upgrade-Insecure-Requests': '1',
    'dnt': '1',
    'te': 'trailers',
}

s = Session()

# send request via mitm proxy and deactivte cert validation
getResponse=s.get("https://laikra.komm.one/dvvlaikraIGV21/servlet/Internetgeschaeftsvorfaelle?AUFRUF=WKZ_lhs", proxies=proxyDict, verify=False)

# Cookie from first Get Request we need for post request
cookies=getResponse.cookies.get_dict()

# Also save timestamp from first request. It seams with a other timestamp server is rejecting post request
soup = BeautifulSoup(getResponse.text , 'html.parser')
timestamp = soup.find('input', {'name': 'ZEITSTEMPEL'}).get('value')

# generate payload
data="""-----------------------------21656587021738608004592965003
Content-Disposition: form-data; name="WKZ_ERKENN_Z"

GO
-----------------------------21656587021738608004592965003
Content-Disposition: form-data; name="WKZ_ZIFFERN"

9??
-----------------------------21656587021738608004592965003
Content-Disposition: form-data; name="WKZ_SUCHMERKMAL"

NULL
-----------------------------21656587021738608004592965003
Content-Disposition: form-data; name="BTN_WKZSUCHE"

suchen
-----------------------------21656587021738608004592965003
Content-Disposition: form-data; name="ZEITSTEMPEL"

{{timestamp}}
-----------------------------21656587021738608004592965003--"""

data = data.replace("{{timestamp}}", timestamp)

postReq = Request(
    'POST', 
    'https://laikra.komm.one/dvvlaikraIGV21/servlet/Internetgeschaeftsvorfaelle',
    data=data,
    cookies = cookies,
    headers = headers
).prepare()

# Print for debug reasons
#print(postReq.headers)
#print(postReq.body.decode('utf-8'))

# send post request using mitm
postRes = s.send(postReq, proxies=proxyDict)
#print(postRes.text)
soup = BeautifulSoup(postRes.text , 'html.parser')
title = soup.find('title').get_text(strip=True)
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