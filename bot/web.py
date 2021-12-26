import requests
import random
from pandas import read_csv
from urllib.parse import quote


class web_accessor:
	"""Reads data from the web."""

	def __init__(self):
		self.session = requests.Session()
		self.max_retries = 3


	def _random_str(self, length:int=-1):
		"""Random string containing a-z A-Z 0-9, by default has random length"""
		if length == -1: length = random.randint(1,32)

		r1 = 90-65+1 #A-Z: 65-90
		r2 = 122-97+1 #a-z: 97-122
		r3 = 57-48+1 #0-9: 48-57
		s = ''
		for i in range(length):
			n = random.randint(1,r1+r2+r3)
			if n <= r1: #A-Z
				n = chr(n+64)
			elif n <= r1+r2: #a-z
				n = chr(n-r1+96)
			else: #0-9
				n = chr(n-r1-r2+47)
			s += n
		return s


	def _read_proxies(self):
		csv = read_csv('bot/data/proxies.csv')
		self.proxies = list("https://"+csv['IP Address']+":"+csv['Port'].astype(str))


	async def web_json(self, url: str, *, params = None):
		"""Reads & returns json of url [requests package]."""
		def get_request(proxy = None):
			headers = {'User-agent': self._random_str()} # random user-agent
			try:
				data = self.session.get(url=url, headers=headers, proxies=proxy, params=params)
				return data.json()
			except Exception as e: #print(f"web_json exception {url=}, {params=}\n{e=}")
				return None

		for i in range(self.max_retries):
			proxy_url = random.choice(self.proxies)
			proxy = {
				"https": proxy_url,
				"http": proxy_url
			}
			out = get_request(proxy)
			if out != None: return out
		return get_request()


	def clean_inputs_for_urls(self, s: str):
		"""Cleans input string to later be passed into a url"""
		return quote(s,safe="")
