#!/usr/bin/python

import urllib.request
import ssl
import pymiwifi
import datetime
import time

miwifi = pymiwifi.MiWiFi()
miwifi.login('xxxxxxxxxx') # Your router password

def telegram(message):
	ssl._create_default_https_context = ssl._create_unverified_context
	# To get this running: 
	# 1. create your bot according to https://gist.github.com/nafiesl/4ad622f344cd1dc3bb1ecbe468ff9f8a#create-a-telegram-bot-and-get-a-bot-token
	# 2. start a chat with your bot
	# 3. Get you chat ID according to https://gist.github.com/nafiesl/4ad622f344cd1dc3bb1ecbe468ff9f8a#get-chat-id-for-a-private-chat 
	data = urllib.parse.urlencode({'chat_id':'XXXXXXXX', 'text': message, 'parse_mode':'MARKDOWN'} ).encode('ascii') # XXXXXX - ID of your private chat with the bot (or channel if you need several recipients)
	urllib.request.urlopen(url = 'https://api.telegram.org/botYYYYYYYY:ZZZZZZZZZZZZZZZZ/sendMessage', data = data ) # YYYYYYYY - bot ID (numbers!), ZZZZZ - bot secret token

def timestamp(content):
	now = datetime.datetime.now()
	date_time = now.strftime("%Y-%m-%d %H:%M:%S")
	print(date_time + " " + str(content))

def getMessage(number, id):
	messageid = {
	"phoneNum": number, 
	"msg_id": id
	}
	return miwifi.post_api_endpoint("xqmobile/get_dialog_msg", messageid)

def delMessage(id):
	messageid = {
	"msgid": id
	}
	return miwifi.post_api_endpoint("xqmobile/delete_msg", messageid)

def sendMessage(number, text):
	content = {
	"contact_phone": number, 
	"msgtext": text
	}
	return miwifi.post_api_endpoint("xqmobile/send_msg", content)

def parseSMS(msg_text):
	message_id = int(msg_text.get('msg_id'))
	message_sender = msg_text.get('contact_phone')
	message_type = int(msg_text.get('state'))
	message_content = msg_text.get('content')
	if (message_type == 9): # if message is type 9, i.e. read, don't process or forward it again
		return None

	if ("Postovani, za surfanje" in message_content) or ("Postovani, za nastavak surfanja" in message_content): # I have to auto-respond to this message, but I choose not to forward it
		sendMessage("13880", "NASTAVI")
	elif ("NASTAVI je u tijeku" in message_content): # ignore this and the following service messages, as they are related to the autoresponder
		pass
	elif ("kad budete trebali poslati" in message_content):
		pass
	elif ("sadrzaja NASTAVI na 13880" in message_content):
		pass
	elif ("u procesu aktivacije" in message_content):
		pass
	elif ("Nastavite slobodno surfati, Internet" in message_content): # this one actually confirms that the autoresponder worked, but it's not forwarded
		pass
	else:
		telegram("SMS from " + message_sender + ":\n*" + message_content + "*") # Forward all other messages
		pass
	timestamp(message_content) # also print them out
	markRead(message_sender, message_id) # mark the message as read

def getMessageCount(): 
	return miwifi.get_api_endpoint("misystem/messages")['count'] # this is the current number of UNREAD messages

def markRead(number, id):
	getMessage(number, id)
	return True

def getMessageBox(): 
	return miwifi.get_api_endpoint("xqmobile/refresh_msgbox") # this endpoint supplies the message content, but doesn't flag the messages as being read

def currentUsage():
	usage = miwifi.get_api_endpoint("xqmobile/get_data_usage_info")['dataUsageInfo']['dataCurUsage'] # The value is formatted as "1.234" (GB) 
	return float(usage)
	
def resetCurrentUsage():
	postdata = {
		'curDataUsage': 0
	}
	return miwifi.post_api_endpoint('xqmobile/set_cur_data_usage', postdata ) # We have to send a "continue" message every 60 gigs, so we reset the counter to zero

def rebootRouter(): # Unused but might come in handy if you need to reboot the router remotely
	postdata = {
		'client': 'web'
	}
	return miwifi.post_api_endpoint('xqsystem/reboot', postdata )

def netInfo():
	return miwifi.get_api_endpoint('xqdtcustom/get_mobile_net_info')['info']
# Sample response {"info":{"linktype":"5G NSA","rsrp":"-95.2","snr":"7.0","cell_band":"B1(FDD 2100)","roam":0,"pci_5g":"874","pci":"418","dl_bw":"15,20,15,100","arfcn":"75,1501,6375,634080","datausage":"0.000","level":4,"freqband":"B1+B3+B20+n78","ci_5g":"-","rsrp_5g":"-93.0","flowstatEnable":1,"registration":1,"dataLimit":"300","operator":"HT HR","planType":"2","snr_5g":"7.0","ul_bw":"15,100","rsrq_5g":"-11.0","cell_band_5g":"n78(TDD 3500)","ci":"38594826","rsrq":"-9.5","pinlock":0}}

def printTraffic():
	traffic = currentUsage()
	timestamp("\tUSAGE: " + '%.2f'%(traffic) + " GB")
	if traffic > 59.5 : # Just in case, I usually send a 'give me another 60 gigs at full speed'-message with some traffic to spare. Remove if not needed.
		sendMessage("13880", "NASTAVI")
		resetCurrentUsage()

def printNetInfo():
	info = netInfo()
	return "\tLINKTYPE: " + info['linktype'] + " BAND: " + info['cell_band'] + " FREQBAND: " + info['freqband']

SkippedLoopsBand = 61 # 60 * 10 = 600 seconds = 10 minutes, but I want to run this loop immediately
SkippedLoopsStats = 31 # 30 * 10 = 300 seconds = 5 minutes

while True:
	if (SkippedLoopsStats >= 30 ): # Let's print out and check the current traffic volume every 5 minutes
		printTraffic()
		SkippedLoopsStats = 0
	else:
		SkippedLoopsStats += 1
	
	if (SkippedLoopsBand >= 60): # Network band info is printed out every 10 minutes
		timestamp(printNetInfo())
		SkippedLoopsBand = 0
	else:
		SkippedLoopsBand += 1

	if getMessageCount() >= 1 :
		messages = getMessageBox()
		for message in messages['msgbox']:
			parseSMS(message)
	time.sleep(10)

