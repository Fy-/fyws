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

	def __init__(self, name):
		self.name = name
		self.users = set()
		self.created = int(time.time())

		FyWSData.add_chan(self)

	def join(self, user):
		user.relatives |= self.users
		self.users.add(user)
		for my_user in self.users:
			my_user.relatives.add(user)
		print('\t\t %s  joined %s' % (user, self))

	def leave(self, user):
		user.relatives ^= self.users
		self.users.discard(user)

		for my_user in self.users:
			my_user.relatives.discard(user)
		print('\t\t %s  left %s' % (user, self))

	async def send(self, data, me=False):
		_users = self.users.copy()
		for _user in _users:
			if _user != self or me == True:
				await _user.send(data)
		del _users

	def __str__(self):
		return '%s (%s), created at %s' % (self.name, len(self.users), self.created)