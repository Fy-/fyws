# -*- coding: utf-8 -*-
from .data import FyWSData
import orjson

class User(object):
	def __init__(self, conn=None):
		self.conn = conn
		self.uuid = self.conn._id+42
		self.auth = False
		self.relatives 	= set()
		self.channels  	= set()
		self.properties = {}
		
		FyWSData.add_user(self)

	async def quit(self):
		_channels = self.channels.copy()
		for channel in _channels:
			await self.leave(channel)

		_relatives = self.relatives.copy()
		for relative in _relatives:
			relative.relatives.discard(self)

		del _relatives

		FyWSData.del_user(self)
		await self.conn.aclose(reason='rq')

	def __str__(self):
		return 'User (%s - %s)' % (self.uuid, self.auth)

	async def join(self, chan):
		if chan not in self.channels:
			self.channels.add(chan)
			await chan.join(self)

	async def leave(self, chan):
		_channels = self.channels.copy()
		if chan in _channels:
			await chan.leave(self)
			self.channels.discard(chan)

	async def send(self, data):
		try:
			await self.conn.send_message(orjson.dumps(data).decode('utf-8'))
		except Exception as e:
			print('\t *** Error sending to %s: %s' % (self, e))
			await self.quit()

	async def send_relatives(self, data, me=True):
		_relatives = self.relatives.copy()
		for relative in _relatives:
			if me == True or relative != self:
				await relative.send(data)
		del _relatives