import threading
import requests
import argparse
import random
import json
import time
import sys
import re
import os

status = {
	'sent': 0,
	'errors': 0,
}

class youtube:
	vid = None
	session = None
	def __init__(self, vid):
		self.vid = vid
		self.session = requests.session()
	
	def getPlayerConfig(self):
		r = self.session.get('https://www.youtube.com/watch?v=' + self.vid, headers={ 
			'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/15E148 Safari/604.1', 
			'Accept': 'image/png,image/svg+xml,image/*;q=0.8,video/*;q=0.8,*/*;q=0.5', 
			'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7', 
			'Referer': 'https://m.youtube.com/watch?v=' + self.vid
		}).text
		if sys.version_info.major < 3:
			r = r.encode('utf-8', 'ignore')
		if 'ytplayer.config' in r:
			data = re.findall(r'ytplayer\.config = (.*);ytplayer\.web_player_context_config', r)
		elif 'ytInitialPlayerConfig' in r:
			data = re.findall(r'ytInitialPlayerConfig = (.*);\n', r)
		data = json.loads(data[0])['args']['player_response']
		player = json.loads(data)
		return player
	
	def getWatchtime(self):
		config = self.getPlayerConfig()
		vanilla = config['playbackTracking']['videostatsWatchtimeUrl']['baseUrl'].replace('\\u0026', '&').replace('%2C', ',')
		cl = vanilla.split("cl=")[1].split("&")[0]
		ei = vanilla.split("ei=")[1].split("&")[0]
		of = vanilla.split("of=")[1].split("&")[0]
		vm = vanilla.split('vm=')[1].split('&')[0]
		return 'https://s.youtube.com/api/stats/watchtime?ns=yt&el=detailpage&cpn=isWmmj2C9Y2vULKF&docid=' + self.vid + '&ver=2&cmt=7334&ei=' + ei + '&fmt=133&fs=0&rt=1003&of=' + of + '&euri&lact=4418&live=dvr&cl=' + cl + '&state=playing&vm=' + vm + '&volume=100&c=MWEB&cver=2.20200313.03.00&cplayer=UNIPLAYER&cbrand=apple&cbr=Safari%20Mobile&cbrver=12.1.15E148&cmodel=iphone&cos=iPhone&cosver=12_2&cplatform=MOBILE&delay=5&hl=ru&cr=GB&rtn=1303&afmt=140&lio=1556394045.182&idpj=&ldpj=&rti=1003&muted=0&st=7334&et=7634'
	
	def watchLive(self, proxy=None):
		global status
		try:
			watch = self.getWatchtime()
			self.session.get(watch, headers={ 
				'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/15E148 Safari/604.1', 
				'Accept': 'image/png,image/svg+xml,image/*;q=0.8,video/*;q=0.8,*/*;q=0.5', 
				'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7', 
				'Referer': 'https://m.youtube.com/watch?v=' + self.vid
			}, proxies=proxy)
			status['sent'] += 1
		except:
			status['errors'] += 1
	
def viewThread(vid, proxy=None):
	proxy = {"https": "https://%s" % proxy} if proxy else None
	youtube(vid).watchLive(proxy)

def statusThread():
	global status
	while True:
		_status = '* sent: %s | errors: %s | total: %s' % (status['sent'], status['errors'], status['sent'] + status['errors'])
		sys.stdout.write('%s\r' % _status)

def formatProxyList(proxy):
	f = open(proxy, 'r')
	l = f.read()
	f.close()
	return [x.rstrip().lstrip() for x in l.splitlines()]

if __name__ == '__main__':
	print('* visualize.py - youtube live viewers bot')
	print('* created by neon // @TheFamilyTeam')
	print('* https://github.com/TheFamilyTeam')
	print('')
	parser = argparse.ArgumentParser(description='youtube live viewers bot - https://github.com/TheFamilyTeam')
	parser.add_argument('--id', '-i', type=str, help='video id', required=True)
	parser.add_argument('--proxy', '-p', type=str, help='proxy file')
	parser.add_argument('--delay', '-d', type=float, help='bot delay')
	args = parser.parse_args()
	
	print('* botting...')
	threading.Thread(target=statusThread).start()
	if args.proxy:
		if not os.path.isfile(args.proxy):
			print('* invalid proxy file')
			exit(1)
		proxies = formatProxyList(args.proxy)
		while True:
			proxy = random.choice(proxies)
			try:
				threading.Thread(target=viewThread, args=(args.id, proxy,)).start()
				time.sleep(0.15 if not args.delay else args.delay)
			except KeyboardInterrupt:
				print('\n* bye!')
				os._exit(0)
	else:
		while True:
			try:
				threading.Thread(target=viewThread, args=(args.id, None,)).start()
				time.sleep(0.15 if not args.delay else args.delay)
			except KeyboardInterrupt:
				print('\n* bye!')
				os._exit(0)
	
	
