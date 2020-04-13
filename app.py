# -*- coding: utf-8 -*-
from trio_websocket import serve_websocket, ConnectionClosed
import datetime
import orjson
from functools import wraps

import ssl
import pathlib


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
		self.callbacks = {}
		self.created = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
		print('*** Flold server, created at %s' % self.created)

	def init_app(self, config={}):
		self.get_config(config)
		
	def register_blueprint(self, blueprint):
		for command in blueprint.commands.keys():
			self.commands[command] = blueprint.commands[command]

	def callback(self, cmd):
		def callable(func):
			@wraps(func)
			def wrapped(*args, **kwargs):
				self.callbacks[cmd] = func
				print('\t registered callback %s (%s)' % (cmd, func))
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
		self.ssl_pem = self.config.get('ssl_pem') or fy_ws_default_config['ssl_pem']

	async def server(self, request):
		ws = await request.accept()
		user = User(ws)
		if self.callbacks.get('on_connect', False):
			await self.callbacks.get('on_connect')(user)
		while True:
			try:
				message = await ws.get_message()
				await self.on_message(user, message)
				# send&co
			except ConnectionClosed:
				if self.callbacks.get('on_quit', False):
					await self.callbacks.get('on_quit')(user)
				user.quit()
				break

	async def run(self):
		await serve_websocket(self.server, self.host, self.port, ssl_context=None)

	async def run_ssl(self):
		ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
		if self.ssl_pem:
			ssl_context.load_cert_chain(self.ssl_pem)

		await serve_websocket(self.server, self.host, self.port, ssl_context=None)

