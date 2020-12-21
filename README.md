# stuttgart-license-plate-scanner

## Setup
* Install Python 3.6+ (due to f-Strings)
* Install `bs4`
* Intall `requests`

## Usage


## Usage with mitm
* Install mitmproxy
* Install mitmproxy cert
* Use Proxy e.g. `scan_license_plates_mitm.py` already use `127.0.0.1:8080`


## Usage with telegram
* set up a bot
* create a group, send a message like `/my_id @my_bot` and find out the chat id via `https://api.telegram.org/bot<TOKEN>/getUpdates`
* test bot and group manually `curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" -d "chat_id=<CHAT_ID>&text=test message from bot"`
