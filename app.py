# -*- coding: utf-8 -*-
from trio_websocket import serve_websocket, ConnectionClosed
import datetime
import orjson
from functools import wraps


from .defaults import fy_ws_default_config
from .user import User

class FyWSBlueprint(object):
	def __init__(self):
		self.commands = {}

	def command(self, cmd):
		def callable(func):
			@wraps(func)
			def wrapped(*args, **kwargs):
				self.commands[cmd] = func
				print('\t registered command %s (%s)' % (cmd, func))
			return wrapped()

		return callable

class FyWS(object):
	def __init__(self):
		self.commands = {}
		self.created = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
		print('*** Flold server, created at %s' % self.created)

	def init_app(self, config={}):
		self.get_config(config)
		
	def register_blueprint(self, blueprint):
		for command in blueprint.commands.keys():
			self.commands[command] = blueprint.commands[command]

	def command(self, cmd):
		def callable(func):
			@wraps(func)
			def wrapped(*args, **kwargs):
				self.commands[cmd] = func
				print('\t registered command %s (%s)' % (cmd, func))
			return wrapped()

		return callable

	async def on_message(self, ws, message):
		data = False
		try:
			data = orjson.loads(message)
		except:
			pass

		if data:
			if 'command' in data and data['command'] in self.commands:
				await self.commands[data['command']](ws, data)

	def get_config(self, config):
		self.config = fy_ws_default_config
		self.host = self.config.get('host') or fy_ws_default_config['host']
		self.port = self.config.get('port') or fy_ws_default_config['port']
		self.debug = self.config.get('debug') or fy_ws_default_config['debug']
		self.ping_timeout = self.config.get('ping_timeout') or fy_ws_default_config['ping_timeout']

	async def server(self, request):
		ws = await request.accept()
		user = User(ws)
		while True:
			try:
				message = await ws.get_message()
				await self.on_message(user, message)
				# send&co
			except ConnectionClosed:
				user.quit()
				break

	async def run(self):
		await serve_websocket(self.server, self.host, self.port, ssl_context=None)