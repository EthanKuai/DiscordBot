from replit import db as database
import os
from datetime import timezone, timedelta


class db_accessor:
	"""Accesses replit database."""

	def __init__(self):
		self._ENV_LST = ['TOKEN','GUILD_ID','DAILY_CHANNEL','DAILY_TIME','TZ_OFFSET','KEY_GOOGLE']
		self._DB_LST = ['LINK_CNT','TIMETABLE_CNT']
		try:
			for i in self._ENV_LST:
				exec(f'self.{i} = os.environ["{i}"]')
				if eval(f'self.{i}').isnumeric(): exec(f'self.{i} = int(self.{i})')
			for i in self._DB_LST:
				exec(f'self.{i} = database["{i}"]')
				if eval(f'self.{i}').isnumeric(): exec(f'self.{i} = int(self.{i})')
		except:
			print("db.__init__: Failed to read environmental variables & database")
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


	def _read_timetables(self):
		"""Read list of users & timetables from database."""
		try:
			self.TIMETABLES = {}
			for i in range(self.TIMETABLE_CNT):
				s = database[f'TIMETABLE{i}'] # <userid>|<contents>
				index = s.find('|')
				assert index != -1 # errors if '|' not found
				assert s[:index].isdigit() # userid is integer
				self.TIMETABLES[int(s[:index])] = s[index+1:] # TIMETABLES[userid] = contents
		except:
			print("db._read_timetables: Failed")
			exit()
		else:
			return True


	def _write_timetables(self):
		"""Overwrites list of users & timetables from database."""
		try:
			if len(self.TIMETABLES) != self.TIMETABLE_CNT:
				raise IndexError("length of TIMETABLES dict != TIMETABLE_CNT")
			database['TIMETABLE_CNT'] = str(self.TIMETABLE_CNT)

			i = 0
			for key, val in self.TIMETABLES.items():
				tmp = str(key) + '|' + val # <userid>|<contents>
				database[f'TIMETABLE{i}'] = tmp
				i += 1
		except:
			print("db._write_timetables: Failed to save timetables to database")
		else:
			return True


	def add_timetable(self, userid: int, contents: str):
		"""Adds or updates list of links, depending on whether it is a new userid."""
		self.TIMETABLES[userid] = contents
		self.TIMETABLE_CNT = len(self.TIMETABLES)
		try:
			self._write_timetables()
		except:
			print("db.add_timetable: Failed to add new timetable")
		else:
			return True


	def _read_links(self):
		"""Read list of links from database."""
		try:
			self.LINKS = []
			for i in range(self.LINK_CNT):
				s = database[f'LINK{i}']
				assert s.startswith('http') # errors if not link
				self.LINKS.append(s)
		except:
			print("db._read_links: Failed")
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
