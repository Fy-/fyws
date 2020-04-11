# -*- coding: utf-8 -*-
from .data import FyWSData
import orjson

class User(object):
	def __init__(self, conn=None):
		self.conn = conn
		self.uuid = self.conn._id
		self.auth = False
		self.relatives 	= set()
		self.channels  	= set()
		FyWSData.add_user(self)

	def quit(self):
		for channel in self.channels:
			channel.users.discard(self)

		_relatives = self.relatives.copy()
		for relative in _relatives:
			relative.relatives.discard(self)

		del _relatives

		FyWSData.del_user(self)

	def __str__(self):
		return 'User (%s - %s)' % (self.uuid, self.auth)

	def join(self, chan):
		if chan not in self.channels:
			self.channels.add(chan)
			chan.join(self)

	def part(self, chan):
		if chan in self.channels:
			self.channels.discard(chan)
			chan.leave(self)

	async def send(self, data):
		r = await self.conn.send_message(orjson.dumps(data).decode('utf-8'))

	async def send_relatives(self, data, me=True):
		_relatives = self.relatives.copy()
		for relative in _relatives:
			if me == True or relative != self:
				await relative.send(data)
		del _relatives