import discord
from discord.ext import commands
import typing

from bot import *
import sys

REDDIT = {"now":"now", "hour":"hour", "day":"day", "daily":"day", "today":"day", "week":"week", "month":"month", "year":"year", "all":"all", "alltime":"all", "overall":"all", "new":"new"}

class RedditCog(commands.Cog):
	"""Reddit"""

	def __init__(self, bot: commands.bot, web_bot: web_accessor):
		self.bot = bot
		self.web_bot = web_bot
		self.MAX_POSTS = 32
		print(sys.argv[0] + ' being loaded!')


	@commands.command(name='reddit', usage=USAGES['reddit']['reddit'], aliases=ALIASES['reddit']['reddit'])
	async def reddit_Command(self, ctx, *, search: str):
		"""Top x posts of a subreddit, default to sort by day."""
		arr = search.split(' ')

		if arr[-1] in REDDIT:
			sortby = REDDIT[arr.pop()]
		else:
			sortby = "day"

		if arr[-1].isnumeric():
			cnt = int(arr.pop())
			cnt = min(max(1, cnt), self.MAX_POSTS)
		else:
			cnt = 5

		sr = '_'.join(arr)
		if len(sr) > 21 or re.search('(^\d)|(^_)',sr):
			raise commands.BadArgument("Invalid subreddit name")

		if sortby == "new":
			link = f'https://reddit.com/r/{sr}/new.json?sort=top&limit={cnt}'
		else:
			link = f'https://reddit.com/r/{sr}/top.json?sort=top&t={sortby}&limit={cnt}'
		messages = await self.web_reddit(link)
		await p(ctx, messages)


	@reddit_Command.error
	async def reddit_Command_error(self, ctx, error):
		await badarguments(ctx, 'reddit', 'reddit')


	async def web_reddit(self, link: str):
		"""reddit API, returns embed messages"""
		data = await self.web_bot.web_json(link)
		data = data['data']['children']
		sr = data[0]['data']['subreddit_name_prefixed']
		lst = [discord.Embed(
			title=f"Reddit's top: {sr}",
			description = "",
			colour=discord.Colour.orange() # change to color of subreddit.
		)]
		img = data[0]['data'].get('url_overridden_by_dest','')
		if len(img) > 4:
			if img[-4:] in [".png", ".jpg", ".jpeg", ".svg", ".mp4"]:
				lst[0].set_image(url=img)

		for i in data:
			link = "https://reddit.com" + i['data']['permalink'].strip()
			score = i['data']['score']
			comments = i['data']['num_comments']
			author = trim(i['data']['author'], 27)
			title = trim(i['data']['title'])
			desc = trim(i['data']['selftext'])

			tmp = f'[**{title}**]({link})\n'
			if desc != '': tmp += desc + '\n'
			tmp += f'Score: {score} Comments: {comments} Author: {author}\n\n'
			if len(lst[-1].description) + len(tmp) > 1900:
				lst[-1].description = lst[-1].description.strip()
				lst.append(discord.Embed(colour=discord.Colour.orange(), description = tmp))
			else:
				lst[-1].description += tmp
		return lst
