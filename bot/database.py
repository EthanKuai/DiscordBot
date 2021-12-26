from replit import db as database
import os
from datetime import timezone, timedelta
from pandas import read_csv


TZ_DICT = dict(read_csv("bot/data/timezones.csv").to_numpy())


class db_accessor:
	"""Accesses replit database."""

	def __init__(self):
		self._ENV_LST = ['TOKEN','GOOGLE_API_ID','GOOGLE_API_KEY','DICTAPI_DICT','DICTAPI_THES']
		self._DB_LST = ['LINK_CNT','GUILD_ID','DAILY_CHANNEL','DAILY_TIME','TZ_OFFSET']
		try:
			for i in self._ENV_LST:
				exec(f'self.{i} = os.environ["{i}"]')
				if eval(f'self.{i}').isnumeric(): exec(f'self.{i} = int(self.{i})')
			for i in self._DB_LST:
				exec(f'self.{i} = database["{i}"]')
				if eval(f'self.{i}').isnumeric(): exec(f'self.{i} = int(self.{i})')
		except Exception as e:
			print("db.__init__: Failed to read environmental variables & database")
			print(e)
			exit()
		self.tz = timezone(timedelta(hours=self.TZ_OFFSET))
		self._read_links()
		self._read_timetables()


	def add_variable_ENV(self, name: str, val, strval: str = ""):
		"""!!!ASSUMES SANITIZED VARIABLE 'name'!!!
		Adds variable to ENV, but not be auto-loaded once program restarts."""
		try:
			assert not (name in self.__dict__) # make sure variable does not already exist
			if strval == "": strval = str(val)

			self._ENV_LST.append(name)
			exec(f'self.{name} = val')
			os.environ[name] = strval
		except:
			print("db.add_variable_ENV: Failed")
		else:
			return True


	def add_variable_DB(self, name: str, val, strval: str = ""):
		"""!!!ASSUMES SANITIZED VARIABLE 'name'!!!
		Adds variable to DB, but not be auto-loaded once program restarts."""
		try:
			assert not (name in self.__dict__) # make sure variable does not already exist
			if strval == "": strval = str(val)

			self._DB_LST.append(name)
			exec(f'self.{name} = val')
			database[name] = strval
		except:
			print("db.add_variable_DB: Failed")
		else:
			return True


	"""TODO: Probably both sets of methods can be condensed with enums, but I dont see an immediate need."""
	"""-------------------------------- timetable --------------------------------"""


	def _read_timetables(self):
		"""Read list of users & timetables from database."""
		self.TIMETABLES = {}
		self.TIMETABLEIMGS = {}
		try:
			# find all matches to 'TIMETABLEX<userid>'
			user_ids = [int(s[10:]) for s in database.prefix("TIMETABLEX")]
			# database['TIMETABLEX<userid>'] = <img_url>|<contents>
			for user_id in user_ids:
				s = database[f'TIMETABLEX{user_id}']
				index = s.find('|')
				assert index != -1 # errors if '|' not found
				assert s[:index] == "" or s[:index].startswith("http")
				self.TIMETABLES[user_id] = s[index+1:] # TIMETABLES[userid] = contents
				self.TIMETABLEIMGS[user_id] = s[:index] # TIMETABLES[userid] = img_url
		except Exception as e:
			print("db._read_timetables: Failed")
			print(e)
			exit()
		else:
			return True


	def _write_timetables(self):
		"""Overwrites list of users & timetables from database."""
		try:
			for user_id, content in self.TIMETABLES.items():
				database[f'TIMETABLEX{user_id}'] = self.TIMETABLEIMGS[user_id] + '|' + content
		except:
			print("db._write_timetables: Failed to save timetables to database")
		else:
			return True


	def add_timetable(self, userid: int, contents: str, *, updated_img: str = None):
		"""Adds or updates list of links, depending on whether it is a new userid."""
		try:
			self.TIMETABLES[userid] = contents
			if updated_img != None: self.TIMETABLEIMGS[userid] = updated_img
			self._write_timetables()
		except:
			print("db.add_timetable: Failed to add new timetable")
		else:
			return True


	"""-------------------------------- daily briefing links --------------------------------"""


	def _read_links(self):
		"""Read list of links from database."""
		try:
			self.LINKS = []
			for i in range(self.LINK_CNT):
				s = database[f'LINK{i}']
				assert s.startswith('http') # errors if not link
				self.LINKS.append(s)
		except Exception as e:
			print("db._read_links: Failed")
			print(e)
			exit()
		else:
			return True


	def _write_links(self):
		"""Overwrites list of links from database."""
		try:
			if len(self.LINKS) != self.LINK_CNT:
				raise IndexError("length of LINKS list != LINK_CNT")
			database['LINK_CNT'] = str(self.LINK_CNT)
			for i in range(self.LINK_CNT):
				database[f'LINK{i}'] = self.LINKS[i]
		except:
			print("db._write_links: Failed to save links to database")
		else:
			return True


	def add_link(self, link: str):
		"""Append list of links."""
		self.LINKS.append(link)
		self.LINK_CNT += 1
		try:
			self._write_links()
		except:
			print("db.add_link: Failed to add new link")
		else:
			return True


	def remove_link(self, link: str):
		"""Removes an existing link from list of links."""
		link = link.strip()
		if link in self.LINKS:
			self.LINK_CNT -= 1
			self.LINKS.remove(link)
			try:
				self._write_links()
			except:
				print("db.remove_link: Failed to remove existing link")
			else:
				return True
		# non-existing link/ failed to remove existing link
		return False


	def update_data(self):
		"""Overwrite all data in database with current data."""
		try:
			self.tz = timezone(timedelta(hours=self.TZ_OFFSET))
			self._write_links()
			self._write_timetables()
			for i in self._ENV_LST:
				os.environ[i] = str(eval(f'self.{i}'))
			for i in self._DB_LST:
				database[i] = str(eval(f'self.{i}'))
		except:
			print("db.update_data: Failed to update environmental variables")
			exit()
		else:
			return True
