# -*- coding: utf-8 -*-
#! /usr/bin/python

import libtcod.libtcodpy as libtcod
import utils
import objects
import client
import sys

def key_handle():
	if ms.active:
		return ms.handle_keys()
	else:
		return cl.handle_keys()

def draw():
	if ms.active:
		ms.draw()
	else:
		cl.draw()

if __name__ == "__main__":
	utils.init_libtcod(objects.ROOT_WIDTH, objects.ROOT_HEIGHT)
	ms = objects.MainScreen()
	while(True):
		draw()
		libtcod.console_flush()
		exit = key_handle()
		if exit == 0:
			break
		elif exit == 1:
			cl = client.Client(ms.data) # "127.0.0.1", "50215"
	sys.exit()