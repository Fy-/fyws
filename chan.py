# -*- coding: utf-8 -*-
from .data import FyWSData
import time

class Chan(object):
	@staticmethod
	def get(name):
		if FyWSData.chans.get(name):
			return FyWSData.chans.get(name)
		else:
			chan = Chan(name)
			return chan

	@staticmethod
	def exists(name):
		if FyWSData.chans.get(name):
			return True
		return False

	def __init__(self, name):
		self.name = name
		self.users = set()
		self.created = int(time.time())
		self.properties = {}
		self.on_join = None
		self.on_leave = None

		FyWSData.add_chan(self)

	async def join(self, user):
		user.relatives |= self.users
		self.users.add(user)
		for my_user in self.users:
			my_user.relatives.add(user)

		if FyWSData.callbacks.get('on_join_chan', False):
			await FyWSData.callbacks.get('on_join_chan')(user, self)

		if self.on_join != None:
			await self.on_join(user, self)

		print('\t\t %s  joined %s' % (user, self))

	async def leave(self, user):
		user.relatives ^= self.users
		self.users.discard(user)

		for my_user in self.users:
			my_user.relatives.discard(user)

		if FyWSData.callbacks.get('on_leave_chan', False):
			await FyWSData.callbacks.get('on_leave_chan')(user, self)

		if self.on_leave != None:
			await self.on_leave(user, self)

		print('\t\t %s  left %s' % (user, self))

		if (len(self.users) == 0):
			FyWSData.del_chan(self)


	async def send(self, data, me=False):
		_users = self.users.copy()
		for _user in _users:
			if _user != self or me == True:
				await _user.send(data)
		del _users

	def __str__(self):
		return '%s (%s), created at %s' % (self.name, len(self.users), self.created)