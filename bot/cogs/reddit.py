import discord
from discord.ext import commands

from bot import *
import sys

REDDIT = {"now":"now", "hour":"hour", "day":"day", "daily":"day", "today":"day", "week":"week", "month":"month", "year":"year", "all":"all", "alltime":"all", "overall":"all"}

class RedditCog(commands.Cog):
	"""Reddit"""

	def __init__(self, bot: commands.bot, web_bot: web_accessor):
		self.bot = bot
		self.web_bot = web_bot
		print(sys.argv[0] + ' being loaded!')


	@commands.command(usage=USAGES['reddit']['reddit'], aliases=ALIASES['reddit']['reddit'])
	async def reddit(self, ctx,
		sr: regex(antireg="\d|\s",maxlen=21),
		cnt: text_or_int(REDDIT) = 5,
		sortby: text_or_int(REDDIT, 0) = "day"
	):
		"""Top x posts of a subreddit, default to sort by day."""
		if isinstance(cnt, str):
			sortby = cnt; cnt = 5
		cnt = min(max(1, cnt),20)
		if sr != "top": sr = 'r/' + sr
		link = f'https://reddit.com/{sr}/top.json?sort=top&t={sortby}&limit={cnt}'
		messages = await self.web_reddit(link)
		await p(ctx, messages)


	@reddit.error
	async def reddit_error(self, ctx, error):
		await badarguments(ctx, 'reddit', 'reddit')


	# reddit API, returns embed messages
	async def web_reddit(self, link: str):
		data = await self.web_bot.web_json(link)
		data = data['data']['children']
		sr = data[0]['data']['subreddit_name_prefixed']
		lst = [discord.Embed(title=f"Reddit's top: {sr}",\
			description = "", colour=discord.Colour.orange())]

		for i in data:
			link = "https://reddit.com" + i['data']['permalink'].strip()
			score = i['data']['score']
			comments = i['data']['num_comments']
			author = trim(i['data']['author'], 27)
			title = "**"+trim(i['data']['title'])+"**"
			desc = trim(i['data']['selftext'])

			tmp = f'[{title}]({link})\n'
			if desc != '': tmp += f'{desc}\n'
			tmp += f'Score: {score} Comments: {comments} Author: {author}\n\n'
			if len(lst[-1].description) + len(tmp) > 1900:
				lst[-1].description = lst[-1].description.strip()
				lst.append(discord.Embed(colour=discord.Colour.orange(), description = tmp))
			else:
				lst[-1].description += tmp
		return lst
