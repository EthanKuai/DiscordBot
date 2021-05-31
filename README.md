# DiscordBot

My personal discord bot to suit my needs. Used in my personal Discord server.

### Motivation

Convenience. Access multiple sites and rng in the comfort of Discord, with 100% privacy.

# Features

- [x] says *hello!*
- [x] reads from [reddit](https://www.reddit.com/), [zenquote](https://zenquotes.io/), [wikipedia](https://en.wikipedia.org/) *and more in the future...*
- [x] dailies set at a fixed time of the day to a fixed channel: contains [daily quotes](https://zenquotes.io/api/today)and reads off a list of links in database (such as daily top reddit posts etc.)
- [x] rng/ coin flip
- [x] echo command to repeat messages
- [x] check Singapore MRT map

### Upcoming Features

- [ ] daily reminder to day/week of year
- [ ] daily backup of server
- [ ] read image & scan for text
- [ ] API connections & pings/updates from *twitter, gnews, merriam webster, etc.*
- [ ] calculator

# Dependencies

List found in [requirements.txt](https://github.com/EthanKuai/DiscordBot/blob/main/requirements.txt)
+ [Python 3.8](https://www.python.org/downloads/release/python-383/)
+ [Discord.py](https://pypi.org/project/discord.py/)
+ [Logging](https://pypi.org/project/logging/)
+ [Flask](https://pypi.org/project/Flask/)
+ [Replit](https://pypi.org/project/replit/)
+ [Asyncpg](https://pypi.org/project/asyncpg/)
+ [Asyncio](https://pypi.org/project/asyncio/)
+ [Requests](https://pypi.org/project/requests/)
+ [Typing](https://pypi.org/project/typing/)

### Installation

	git clone https://github.com/EthanKuai/DiscordBot.git
	cd DiscordBot
	python -m pip install --upgrade pip
 	if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Usage

List of commands found in [bot/help.json](https://github.com/EthanKuai/DiscordBot/blob/main/bot/help.json)
*! Will do full list in the future*
