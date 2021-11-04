import requests
import random


class web_accessor:
	"""Reads data from the web."""

	def __init__(self):
		self.session = requests.Session()

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

	async def web_json(self, url: str, params = False):
		"""Reads & returns json of url [requests package]."""
		headers = {'User-agent': self._random_str()} # random user-agent

		try:
			if not params:
				data = self.session.get(url=url, headers=headers)
			else:
				data = self.session.get(url=url, headers=headers, params=params)
			return data.json()
		except Exception as e:
			print(f"web_json exception {url=}, {params=}\n{e=}")
