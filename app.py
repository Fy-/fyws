# -*- coding: utf-8 -*-
from trio_websocket import serve_websocket, ConnectionClosed
import datetime
import orjson
from functools import wraps
import ssl, sys, traceback
from .defaults import fy_ws_default_config
from .user import User
from .data import FyWSData

class FyWSBlueprint(object):
	def __init__(self):
		self.commands = {}
		self.callbacks = {}

	def command(self, cmd):
		def callable(func):
			@wraps(func)
			def wrapped(*args, **kwargs):
				self.commands[cmd] = func
				print('\t registered command %s (%s)' % (cmd, func))
			return wrapped()

		return callable

	def callback(self, cmd):
		def callable(func):
			@wraps(func)
			def wrapped(*args, **kwargs):
				self.callbacks[cmd] = func
				print('\t registered callback %s (%s)' % (cmd, func))
			return wrapped()

		return callable

class FyWS(FyWSBlueprint):
	def __init__(self):
		self.commands = {}
		self.callbacks = {}
		self.created = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
		print('*** Flold server, created at %s' % self.created)

	def init_app(self, config):
		self.get_config(config)
		for command in self.commands.keys():
			FyWSData.commands[command] = self.commands[command]

		for callback in self.callbacks.keys():
			FyWSData.callbacks[callback] = self.callbacks[callback]

	def register_blueprint(self, blueprint):
		for command in blueprint.commands.keys():
			FyWSData.commands[command] = blueprint.commands[command]

		for callback in blueprint.callbacks.keys():
			FyWSData.callbacks[callback] = blueprint.callbacks[callback]

	async def on_message(self, ws, message):
		data = False
		try:
			data = orjson.loads(message)
		except:
			pass

		if data:
			if 'command' in data and data['command'] in FyWSData.commands:
				try:
					await FyWSData.commands[data['command']](ws, data)
				except Exception as e:
					exc_type, exc_value, exc_traceback = sys.exc_info()
					print('\t *** Error on command %s - %s' % (data, e))
					traceback.print_tb(exc_traceback, file=sys.stdout)

	def get_config(self, config):
		self.config = config
		self.host = self.config.get('host') or fy_ws_default_config['host']
		self.port = self.config.get('port') or fy_ws_default_config['port']
		self.debug = self.config.get('debug') or fy_ws_default_config['debug']
		self.ssl_pem = self.config.get('ssl_pem', False)

	async def server(self, request):
		ws = await request.accept()
		user = User(ws)
		if FyWSData.callbacks.get('on_connect', False):
			await FyWSData.callbacks.get('on_connect')(user)
		while True:
			try:
				message = await ws.get_message()
				await self.on_message(user, message)
			except ConnectionClosed:
				break
			except Exception as e:
				exc_type, exc_value, exc_traceback = sys.exc_info()
				print('\t *** Unknown error %s' %e)
				traceback.print_tb(exc_traceback, file=sys.stdout)

				break

		if FyWSData.callbacks.get('on_quit', False):
			await FyWSData.callbacks.get('on_quit')(user)

		await user.quit()

	async def run(self):
		await serve_websocket(self.server, self.host, self.port, ssl_context=None)

	async def run_ssl(self):
		ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
		ssl_context.load_cert_chain(self.ssl_pem)
		await serve_websocket(self.server, self.host, self.port, ssl_context=ssl_context)

