import urllib.parse
import requests
import json
import os
from subprocess import Popen, PIPE
import time
import pprint
import os
if not os.path.exists("music"):
	os.mkdir("music")

channelID = "C7H8KHS69"
#test channel : channelID = "C7HQXCU21"
token = open('token','r').read().rstrip('\n').rstrip('\r')

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

def playLocalMusic(music_path):
	path = "music/" + music_path
	global mplayer
	pipes = dict(stdin=PIPE, stdout=PIPE, stderr=PIPE)
	mplayer = Popen(["mplayer", path], **pipes)

def recieveSlackData():
	par = urllib.parse.urlencode({
		'token':token,
		'channel':channelID,
		'count':1
	})
	res = requests.get("https://slack.com/api/channels.history",params=par)
	data = json.loads(res.text)
	return data

def sendMessage(text):
        par = urllib.parse.urlencode({
                'token':token,
                'channel':channelID,
                'text':text
        })
        res = requests.get("https://slack.com/api/chat.postMessage",params=par)

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
		return False

music_data_list = []

onryo = 100

mplayer_terminated = False

while True:
	# print("loop")
	# Check Slack
	try:
		data = recieveSlackData()
	except:
		print('cant get data!')
	if checkUpdate(data):

		# 曲をストックに追加
		if isMusicData(data):
			music_data_list.append(getMusicData(data))
			sendMessage("再生リスト")
			for cnt, music_data in enumerate(music_data_list):
				sendMessage(str(cnt+1)+": "+music_data[0].split('.')[0])

		text = data["messages"][0]["text"]

		# 音量を上げる
		if text == 'up' and onryo != 100:
			onryo = onryo + 5
			os.system('amixer cset numid=1 '+str(onryo)+'%')
			sendMessage("Set "+str(onryo)+"%")

		# 音量を下げる
		if text == 'down' and onryo != 85:
			onryo = onryo - 5
			os.system('amixer cset numid=1 '+str(onryo)+'%')
			sendMessage("Set "+str(onryo) + "%")

		# スキップ
		if mplayer and text == 'skip':
			mplayer.terminate()
			mplayer_terminated = True

		# 停止
		if mplayer and text == 'stop':
			music_data_list = []
			mplayer.terminate()
			mplayer_terminated = True

		# スリープ
		if mplayer and text.split(' ')[0] == 'urusai':
			mplayer.terminate()
			print(float(text.split(' ')[1]) * 60)
			time.sleep(float(text.split(' ')[1]) * 60)
			mplayer_terminated = True

		# show list
		if text == 'list':
			musics = os.listdir('./music')
			musics = [ s.replace('.m4a','') for s in musics]
			s = '\n'.join(musics)
			sendMessage(s)

		# Kyokumei kara add
		if text.split(' ')[0] == 'refrain':
			music = text.split(' ')[1] + '.m4a'
			music_data_list.append(['refrain',music])
			sendMessage("再生リスト")
			for cnt, music_data in enumerate(music_data_list):
				sendMessage(str(cnt+1)+": "+music_data[1].split('.')[0])			

	# 曲が流れていなければ、ストックから曲を取り出して再生
	if (isMusicStop() or mplayer_terminated) and music_data_list:
		mplayer_terminated = False
		music_data = music_data_list.pop(0)
		if music_data[0] == 'refrain':
			# play local
			sendMessage("Now playing: "+music_data[1].split('.')[0])
			playLocalMusic(music_data[1])
		else:
			sendMessage("Now playing: "+music_data[0].split('.')[0])
			playMusic(music_data)

	# Wait 1 sec
	time.sleep(1)
