import discord
from discord.ext import commands

from bot import *
from disputils import BotEmbedPaginator
from googletrans import Translator
# python -m pip install googletrans==4.0.0-rc1


class GoogleCog(commands.Cog):
	"""Google & Various Searches"""

	def __init__(self, bot: commands.bot, db: db_accessor, web_bot: web_accessor):
		self.bot = bot
		self.db = db
		self.web_bot = web_bot
		self.translator = Translator(service_urls=['translate.googleapis.com'])
		self.google_logo = "https://www.pngall.com/wp-content/uploads/5/Google-G-Logo-PNG-Image.png"
		self.translate_logo = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Google_Translate_logo.svg/1024px-Google_Translate_logo.svg.png"
		self.url = "https://www.googleapis.com/customsearch/v1"
		self.MAX_SEARCH = 5


	@commands.command(usage=USAGES['google']['google'], aliases=ALIASES['google']['google'])
	async def google(self, ctx, *, search: str):
		"""Google Search. Please use sparringly."""
		embeds = await self.web_google(search)
		paginator = BotEmbedPaginator(ctx, embeds)
		await paginator.run(timeout = PAGINATOR_TIMEOUT)


	@google.error
	async def google_error(self, ctx, error):
		await badarguments(ctx, 'google', 'google')


	# https://developers.google.com/custom-search/v1/using_rest
	async def web_google(self, search: str):
		embeds = []
		try:
			params = {
				"key": self.db.GOOGLE_API_KEY,
				"cx": self.db.GOOGLE_API_ID,
				"q": self.web_bot.clean_inputs_for_urls(search),
				"start": 1, # pg=-2, start=11; page=3, start=21
				"num": self.MAX_SEARCH
			}
			json = await self.web_bot.web_json(self.url, params = params)
			json = json["items"]

			for entry in json:
				title = trim(entry["title"])
				link = process_links(entry["link"])
				displayLink = trim(entry["displayLink"])
				snippet = trim(entry["snippet"], MAX_FIELD-len(displayLink))
				img = entry.get("pagemap", {}).get("cse_image", [{"src":""}])[0]["src"]
				if not img.startswith("http"): img = ""

				embeds += [
					discord.Embed(
						title = title,
						url = link,
						description = f"*{displayLink}*\n\n{snippet}",
						color = discord.Colour.blue()
					)
					.set_author(name = "Google", icon_url = self.google_logo)
					.set_image(url = img)
				]
			return embeds

		except Exception as e:
			print(f"web_google exception {search=}\n{e=}\n{embeds=}")


	@commands.command(usage=USAGES['google']['googletranslate'], aliases=ALIASES['google']['googletranslate'])
	async def googletranslate(self, ctx, lang: regex(reg="[A-z\-]+"), *, untranslated: str):
		"""Google translates from (auto-detect language) to specified language"""
		if lang.lower() in ["ch","cn","zhcn","zh-cn"]: lang = "zh-CN"
		elif lang.lower() in ["zh","tw","zhtw","zh-tw"]: lang = "zh-TW"
		translated = self.translator.translate(untranslated, dest = lang)

		embed = [
			discord.Embed(
				title = "Google Translate",
				url = f"https://translate.google.com.sg/?sl=auto&tl={lang}&text={self.web_bot.clean_inputs_for_urls(untranslated)}&op=translate",
				color = discord.Color.green()
			)
			.set_author(name = "Google Translate", icon_url = self.translate_logo)
			.add_field(name = "Untranslated", value = untranslated[:MAX_FIELD], inline = True)
			.add_field(name = "Translated", value = translated[:MAX_FIELD], inline = True)
		]
		await p(ctx, embed)


	@googletranslate.error
	async def googletranslate_error(self, ctx, error):
		await badarguments(ctx, 'google', 'googletranslate')


"""
#current method
#https://www.thepythoncode.com/article/use-google-custom-search-engine-api-in-python
#https://developers.google.com/custom-search/v1/overview
#https://cse.google.com/cse/setup/basic
#https://stackoverflow.com/questions/37083058/programmatically-searching-google-in-python-using-custom-search


#funny method which requires manual sign-in so im not using it
#https://developers.google.com/webmaster-tools/search-console-api-original/v3/quickstart/quickstart-python
#https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid
#https://console.cloud.google.com/apis/credentials

from apiclient import errors
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
import httplib2

	def setup2(self):
		# Check https://developers.google.com/webmaster-tools/search-console-api-original/v3/ for all available scopes
		self.OAUTH_SCOPE = 'https://www.googleapis.com/auth/webmasters.readonly'

		# Redirect URI for installed apps
		self.REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

		# Run through the OAuth flow and retrieve credentials
		flow = OAuth2WebServerFlow(self.db.GOOGLE_CLIENTID, self.db.GOOGLE_CLIENTSECRET, self.OAUTH_SCOPE, self.REDIRECT_URI)
		authorize_url = flow.step1_get_authorize_url()
		print('Go to the following link in your browser: ' + authorize_url)
		code = raw_input('Enter verification code: ').strip()
		credentials = flow.step2_exchange(code)

		# Create an httplib2.Http object and authorize it with our credentials
		http = httplib2.Http()
		http = credentials.authorize(http)

		webmasters_service = build('searchconsole', 'v1', http=http)

		# Retrieve list of properties in account
		site_list = webmasters_service.sites().list().execute()

		# Filter for verified websites
		verified_sites_urls = [s['siteUrl'] for s in site_list['siteEntry']
							if s['permissionLevel'] != 'siteUnverifiedUser'
								and s['siteUrl'][:4] == 'http']

		# Print the URLs of all websites you are verified for.
		for site_url in verified_sites_urls:
			print(site_url)
			# Retrieve list of sitemaps submitted
			sitemaps = webmasters_service.sitemaps().list(siteUrl=site_url).execute()
			if 'sitemap' in sitemaps:
				sitemap_urls = [s['path'] for s in sitemaps['sitemap']]
				print("  " + "\n  ".join(sitemap_urls))
"""
