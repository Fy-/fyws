# -*- coding: utf-8 -*-
class FyWSData(object):
	all_users = {}
	logged_users = {}
	chans = {}
	callbacks = {}
	commands = {}

	@staticmethod
	def add_user(user):
		print('\t new user: %s' % user)
		FyWSData.all_users[user.uuid] = user

	@staticmethod
	def del_user(user):
		print('\t del user: %s' % user)
		if user.uuid in FyWSData.all_users:
			del FyWSData.all_users[user.uuid]

	@staticmethod
	def add_chan(chan):
		print('\t new chan: %s' % chan)
		FyWSData.chans[chan.name] = chan

	@staticmethod
	def del_chan(chan):
		print('\t del chan: %s' % chan)
		if chan.name in FyWSData.chans:
			del FyWSData.chans[chan.name]

