import discord
from discord.ext import commands
import typing

from bot import *
from disputils import BotEmbedPaginator


REDDIT = {"now":"now", "hour":"hour", "day":"day", "daily":"day", "today":"day", "week":"week", "month":"month", "year":"year", "all":"all", "alltime":"all", "overall":"all", "new":"new"}

class RedditCog(commands.Cog):
	"""Reddit"""

	def __init__(self, bot: commands.bot, web_bot: web_accessor):
		self.bot = bot
		self.web_bot = web_bot
		self.MAX_POSTS_INDIV = 18
		self.MAX_POSTS = 32
		self.reddit_logo = "https://logodownload.org/wp-content/uploads/2018/02/reddit-logo-16.png"


	@commands.command(name='reddit', usage=USAGES['reddit']['reddit'], aliases=ALIASES['reddit']['reddit'])
	async def reddit_Command(self, ctx, *, search: str):
		"""Top x posts of a subreddit, default to sort by day."""
		arr = search.split(" ")

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

		if sr in ["top", "main", "reddit"]:
			sr = "top"
			link = f'https://www.reddit.com/top.json?sort=top&t={sortby}&limit={cnt}'
		elif sortby == "new":
			link = f'https://reddit.com/r/{sr}/new.json?sort=top&limit={cnt}'
		else:
			link = f'https://reddit.com/r/{sr}/top.json?sort=top&t={sortby}&limit={cnt}'

		if cnt > self.MAX_POSTS_INDIV:
			embeds = await self.web_reddit(link, indiv_posts = False, top = (sr == "top"))
		else:
			embeds = await self.web_reddit(link, indiv_posts = True, top = (sr == "top"))
		paginator = BotEmbedPaginator(ctx, embeds)
		await paginator.run()


	@reddit_Command.error
	async def reddit_Command_error(self, ctx, error):
		await badarguments(ctx, 'reddit', 'reddit')


	async def web_reddit(self, link: str, *, indiv_posts: bool = False, top: bool = False):
		"""reddit API, returns embed messages"""
		imgs = [] # valid image links
		lst = [""] # segmented description for main embed
		try:
			data = await self.web_bot.web_json(link)
			data = data['data']['children']

			# for main embed
			if top:
				sr_main = 'Top posts reddit-wide'
				link_main = f"https://www.reddit.com/"
			else:
				sr_main = data[0]['data']['subreddit_name_prefixed']
				link_main = f"https://www.reddit.com/{sr_main}/"

			if indiv_posts: indiv_embeds = [] # indiv embeds

			for i in data:
				link = "https://reddit.com" + i['data']['permalink'].strip()
				score = i['data']['score']
				comments = i['data']['num_comments']
				author = trim(i['data']['author'], MAX_FIELD)
				title = trim(i['data']['title'])
				desc = trim(i['data']['selftext'])
				sr = i['data']['subreddit_name_prefixed']
				# img, to append to imgs if valid
				img = i['data'].get('url_overridden_by_dest','')
				if len(img) > 4 and img[-4:] in IMG_TYPES: imgs.append(img)
				else: img = ""

				# formatting indiv embed
				if indiv_posts:
					tmp = f'Score: {score} Comments: {comments} Author: {author}\n'
					tmp += trim(i['data']['selftext'], MAX_LEN)
					indiv_embeds.append(
						discord.Embed(
							title = title,
							url = link,
							colour = discord.Colour.orange()
						)
						.add_field(name = "Score", value = score, inline = True)
						.add_field(name = "Comments", value = comments, inline = True)
						.add_field(name = "Author", value = author, inline = True)
						.set_author(
							name = "Reddit: " + sr,
							icon_url = self.reddit_logo,
							url = f"https://www.reddit.com/{sr}/"
						)
						.set_image(url=img)
					)
					if desc != '':
						indiv_embeds[-1].add_field(
							name = "Description",
							value = trim(i['data']['selftext'], MAX_FIELD),
							inline = False
						)

				# formatting main embed
				tmp = process_links(f'[**{title}**]({link} )') + '\n'
				if desc != '': tmp += desc + '\n'
				tmp += f'Score: {score} Comments: {comments} Author: {author}\n\n'

				if len(lst[-1]) + len(tmp) > MAX_LEN: lst.append(tmp)
				else: lst[-1] = lst[-1] + tmp

			imgs += [""] * len(lst)
			main_embeds = [
				discord.Embed(
					title = sr_main,
					url = link_main,
					description = x,
					colour = discord.Colour.orange() # change to color of subreddit.
				)
				.set_author(name = "Reddit", icon_url = self.reddit_logo)
				.set_image(url=imgs.pop(0))
				for x in lst
			]

			if indiv_posts: main_embeds += indiv_embeds
			return main_embeds

		except Exception as e:
			print(f"web_reddit exception {link=}\n{e=}\n{lst=}")
