from replit import db as database
import os
from datetime import timezone, timedelta


class db_accessor:
	def __init__(self):
		self.ENV_LST = ['TOKEN','GUILD_ID','DAILY_CHANNEL','DAILY_TIME','TZ_OFFSET','KEY_GOOGLE']
		self.DB_LST = []
		try:
			for i in self.ENV_LST:
				exec(f'self.{i} = os.environ["{i}"]')
				if eval(f'self.{i}').isnumeric(): exec(f'self.{i} = int(self.{i})')
			for i in self.DB_LST:
				exec(f'self.{i} = database["{i}"]')
				if eval(f'self.{i}').isnumeric(): exec(f'self.{i} = int(self.{i})')
		except:
			print("db.__init__: Failed to read environmental variables & database")
			exit()
		self.tz = timezone(timedelta(hours=self.TZ_OFFSET))
		self.read_links()

	def read_links(self):
		try:
			self.LINK_CNT = int(database['LINK_CNT'])
			self.LINKS = []
			for i in range(self.LINK_CNT):
				self.LINKS.append(database[f'LINK{i}'])
		except:
			print("db.read_links: Failed")
			exit()

	def save_links(self):
		try:
			if len(self.LINKS) != self.LINK_CNT:
				raise IndexError("length of LINKS array != LINK_CNT")
			database['LINK_CNT'] = str(self.LINK_CNT)
			for i in range(self.LINK_CNT):
				database[f'LINK{i}'] = self.LINKS[i]
		except:
			print("db.save_links: Failed to save links to database")
			exit()

	def add_link(self, link: str):
		self.LINKS.append(link)
		self.LINK_CNT += 1
		try:
			self.save_links()
		except:
			print("db.write_links: Failed to write new link to database")
			exit()

	def update_data(self):
		try:
			self.tz = timezone(timedelta(hours=self.TZ_OFFSET))
			self.save_links()
			for i in self.ENV_LST:
				os.environ[i] = str(exec(f'self.{i}'))
		except:
			print("db.update_data: Failed to update environmental variables")
			exit()
