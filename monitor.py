import requests
import random
import time
import discord
from time import localtime
from copy import deepcopy
from bs4 import BeautifulSoup as bs

linkembed = {
  "embeds": [
	{
	  "title": "Stadium Goods: New Time Found!",
	  "description": "Try here: https://stadiumgoods.as.me/schedule.php \n \n \n"
	}
  ]
}

def pick_proxy(proxies):
	p = random.choice(proxies)
	arr = p.split(":")
	p_http = None
	p_https = None
	if len(arr) == 2:
		p_https = "https://" + arr[0] + ":" + arr[1]
	else:
		p_https = "https://" + arr[2] + ":" + arr[3] + "@" + arr[0] + ":" + arr[1]
	if len(arr) == 2:
		p_http = "http://" + arr[0] + ":" + arr[1]
	else:
		p_http = "http://" + arr[2] + ":" + arr[3] + "@" + arr[0] + ":" + arr[1]
	proxy = {
		"http": p_http,
		"https": p_https,
	}
	return proxy


def sendDiscord(webhook):
	for retry in range(5):
		try:
			r = requests.post(url=webhook, json=linkembed)
			r.raise_for_status()
		except requests.exceptions.HTTPError as http_err:
			print(f'HTTP error occurred: {http_err}')  # Python 3.6
			if (r.status_code == 429):
				retrydelay = r.json()['retry_after'] / 1000
				time.sleep(retrydelay)
			else:
				time.sleep(1)
			pass
		except Exception as err:
			print(f'Other error occurred: {err}')  # Python 3.6
			time.sleep(1)
			pass
		else:
			break


def getSitemap(proxies):
	headers = {
		'authority': 'stadiumgoods.as.me',
		'accept': '*/*',
		'dnt': '1',
		'x-requested-with': 'XMLHttpRequest',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
		'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'origin': 'https://stadiumgoods.as.me',
		'sec-fetch-site': 'same-origin',
		'sec-fetch-mode': 'cors',
		'sec-fetch-dest': 'empty',
		'referer': 'https://stadiumgoods.as.me/schedule.php',
		'accept-language': 'en-US,en;q=0.9,es;q=0.8'
	}

	params = (
		('action', 'showCalendar'),
		('fulldate', '1'),
		('owner', '19747789'),
		('template', 'weekly'),
	)

	data = {
	  'type': '15068151',
	  'calendar': '4111854',
	  'skip': 'true',
	  'options[qty]': '1',
	  'options[numDays]': '5',
	  'ignoreAppointment': '',
	  'appointmentType': '',
	  'calendarID': ''
	}
	for retry in range(10):
		try:
			r = requests.post('https://stadiumgoods.as.me/schedule.php', headers=headers, params=params, data=data, proxies=pick_proxy(proxies), timeout=20)
			if (r.status_code == 200):
				return r.content
		except Exception as e:
			print(e)
			pass
	else:
		return None
		
def isTimeAvailable(htmlcontent):
	if (htmlcontent is not None):
		soup = bs(htmlcontent, 'html.parser')
		notimes = soup.find("span", {"id":"no-times-available-message"})
		if (notimes == None):
			return True
		else:
			return False
	else:
		return False


if __name__ == "__main__":
	proxies = []
	webhook = "https://discordapp.com/api/webhooks/734451228058189855/ns4UT6Hu9HpEgxjMuDENnqOfmNah9Ppk1604WQqnX-9WVu-mjVwYOdWfAg_UecIVFfqq"

	with open("proxies.txt", "r") as f:
		proxies = f.read().splitlines()
		f.close()

	oldtimes = isTimeAvailable(getSitemap(proxies))
	
	while True:
		currenttime = time.strftime("[%d %b %H:%M:%S]", localtime())
		newtimes = isTimeAvailable(getSitemap(proxies))
		print(currenttime + " Schedule received. Checking for restock...")
		print(oldtimes)
		print(newtimes)
		if (oldtimes == False and newtimes == True):
			sendDiscord(webhook)
		oldtimes = newtimes
		time.sleep(1)