# stuttgart-license-plate-scanner
Collection of python scripts to query available license plates in Stuttgart, Germany.

The Scripts basically settle on `bs4` and `requests`.
If you wish to get Notifications also Scripts to send the results to telegram are available.

## Basic Setup
* Install Python 3.6+ (due to f-Strings)
* Install `bs4` e.g. via `pip install bs4`
* Install `requests` e.g. via `pip install requests`
* Install `pytz` e.g. via `pip install pytz`
* Install `python-telegram-bot` e.g. via `pip install python-telegram-bot`

## Usage of plain
`scan_license_plates.py` is a basic example. It needs no further dependencies as the basic Setup.

### Execution
To scan S:GO-9?? run `python scan_license_plates.py --letters go --numbers 9??`

## Usage with mitm
`scan_license_plates_mitm.py` uses a proxy which can be `mitm` to capture the traffic.
### Setup
* Install mitmproxy
* Install mitmproxy cert on your System
* Use mitm Proxy like in script `scan_license_plates_mitm.py` which already uses `127.0.0.1:8080`

### Excution
To scan S:GO-9?? run `python scan_license_plates_telegram.py --letters go --numbers 9??`

## Usage with telegram
`scan_license_plates_telegram.py` queries the wanted license plate and send the results via telegram bot to a chat.

### Setup bot
* set up a bot
* create a group, send a message like `/my_id @my_bot` and find out the chat id via `https://api.telegram.org/bot<TOKEN>/getUpdates`
* test bot and group manually `curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" -d "chat_id=<CHAT_ID>&text=test message from bot"`

### Setup Python
* install `python-telegram-bot` e.g. via `pip install python-telegram-bot`

### Execution
To scan S:GO-9?? and get a message run `python scan_license_plates_telegram.py --letters go --numbers 9?? --telegram-bot-token <TOKEN> --telegram-chat-id <CHAT_ID>`

## Usage with telegram bot
`scan_multiple_license_plates_telegram.py` scans for multiple plate combinations at once at given timestamps. Can also process commands served to the telegram bot. Given timestamps are interpreted in Berlin Timezone.

`python scan_multiple_license_plates_telegram.py --combination ab:123 --combination bc:456 --combination cd:789 -t 09:00:00 -t 12:00:00 -t 15:00:00 -t 18:00:00 --telegram-bot-token <TOKEN> --telegram-chat-id <CHAT_ID>`

### Bot Commands
* `/help` to show available commands
* `/scanAll` trigger search for configured combinations
* `/scan <combination>` trigger search for given combination (<letters>:<numbers>). multiple combinations are possible.
* `/butterfly` Easteregg, sending some random pictures from the image folder


# Docker
* `docker build --progress=plain --no-cache -t licence .`