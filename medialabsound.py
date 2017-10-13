import urllib.parse
import requests
import json
import os
from subprocess import Popen, PIPE
import time
import pprint
import os
os.mkdir("music")

#channelID = "C7H8KHS69"
channelID = "C7HQXCU21"
token = open('token','r').read().rstrip('\n').rstrip('\r\n')

mplayer = []

def playMusic(music_data):
	[title, link] = music_data
	path = "music/" + title
	global mplayer
	r = requests.get(link, headers={'Authorization': 'Bearer %s' % token})
	if r.status_code != 200:
		raise Exception("Cannot connected Slack server!")
	with open(path, 'wb') as f:
		for chunk in r:
			f.write(chunk)
	pipes = dict(stdin=PIPE, stdout=PIPE, stderr=PIPE)
	mplayer = Popen(["mplayer", path], **pipes)

def getSlackData():
	par = urllib.parse.urlencode({
		'token':token,
		'channel':channelID,
		'count':1
	})
	res = requests.get("https://slack.com/api/channels.history",params=par)
	data = json.loads(res.text)
	return data

def isMusicData(data):
	if "subtype" in data["messages"][0] and data["messages"][0]["subtype"] == "file_share":
		return True
	else:
		return False

def getMusicData(data):
	title = data["messages"][0]["file"]["name"]
	link = data["messages"][0]["file"]["url_private_download"]
	return [title, link]

pre_data = []
def checkUpdate(data):
	global pre_data
	if pre_data == data:
		return False
	pre_data = data
	return True

def isMusicStop():
	if not mplayer or (mplayer and mplayer.poll() == 0):
		return True
	else:
		print("false")
		return False

music_data_list = []

while True:
	print("loop")
	# Check Slack
	data = getSlackData()
	if checkUpdate(data):
		print("a")
		if isMusicData(data):
			print("aa")
			music_data_list.append(getMusicData(data))
			print("Now stashed")
			for cnt, music_data in enumerate(music_data_list):
				print(str(cnt+1)+": "+music_data[0].split('.')[0])

	# Play music
	if isMusicStop() and music_data_list:
		music_data = music_data_list.pop(0)
		print("Play: "+music_data[0].split('.')[0])
		playMusic(music_data)

	# Wait 1 sec
	time.sleep(1)
