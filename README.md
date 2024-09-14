# pyMiWiFi SMS forwarder

A use case for pyMiWiFi that forwards SMS messages received by a Xiaomi MiWifi router to a Telegram bot.
Tested on Xiaomi 5G CPE CB0401V2 (HW1.0)

Bonus API endpoint examples: 
* deleting messages
* detailed network stats and network band information
* traffic volume monitoring

Bonus feature:
* SMS autoresponder (a local mobile provider has an "unlimited" package which requires one to send a text message every X gigabytes for unlimited speed)

## Install

`git clone https://github.com/biuklija/pymiwifi-SMS-forwarder.git`

Python >= 3.6 

## Setup and use

1. Add your router password
2. Set up your Telegram bot, edit the tokens, set the user/chat ID where you intend to receive the forwarded messages
3. Adjust timings in the main loop as needed
4. Remove or add any function calls you (don't) need
5. If necessary, hardcode the router IP or edit the miwifi.com endpoint in `api.py`
6. Run `mifwd.py`