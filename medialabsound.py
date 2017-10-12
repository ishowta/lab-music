import urllib.parse
import requests
import json
import os
import pygame
from playsound import playsound
import shutil
#from mplayer import Player
from subprocess import Popen, PIPE

channelID = "C7H8KHS69"
token = open('token','r').read()

#pygame.mixer.init()

pre_title = ""

def getData():
	global pre_title
	par = {
		'token':token,
		'channel':channelID,
		'count':1
	}

	par = urllib.parse.urlencode(par)
	res = requests.get("https://slack.com/api/channels.history",params=par)
	#req.add_header('Content-Type', 'application/x-www-form-urlencoded')
	#req.add_data(params)
	#res = urllib3.urlopen(req)
	#print(res.text)
	data = json.loads(res.text)
	link = data["messages"][0]["file"]["url_private_download"]
	title = data["messages"][0]["file"]["name"]
	if title != pre_title:
		pre_title = title
		print(link)
		print(title)
		r = requests.get(link, headers={'Authorization': 'Bearer %s' % token})
		if r.status_code == 200:
			print('200 OK')
			with open(title, 'wb') as f:
				#r.raw.decode_content = true
				#shutil.copyfileobj(r.raw, f)
				for chunk in r:
					f.write(chunk)
		pipes = dict(stdin=PIPE, stdout=PIPE, stderr=PIPE)
		mplayer = Popen(["mplayer", title], **pipes)
		mplayer.communicate(input=b">")
		#sys.stdout.flush()
		#player = Player()
		#player.loadfile(title)
		#os.system("wget -O "+title+" "+link)
		#playsound(title)
		#pygame.mixer.music.load(title)
		#pygame.mixer.music.play()
		#while pygame.mixer.music.get_busy() == True:
		#	continue
		print("finish run")
while True:
	getData()
