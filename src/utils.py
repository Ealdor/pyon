# -*- coding: utf-8 -*-

import sys
import cPickle as pickle
import struct

import libtcod.libtcodpy as libtcod

def init_libtcod(width, height):
	libtcod.console_set_custom_font("./fonts/10x10.png", libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, 16, 48)
	libtcod.console_init_root(width, height, "pyon", False, libtcod.RENDERER_SDL)
	libtcod.sys_set_fps(30)

# prefix each message with a 4-byte length (network byte order)
def send_msg(sock, msg):
    data = pickle.dumps(msg, -1)
    msg = struct.pack('>I', len(data)) + data
    sock.sendall(msg)

def recv_msg(sock):
    raw_msglen = recvall(sock, 4) # read message length and unpack it into an integer
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    return pickle.loads(recvall(sock, msglen)) # read the message data

# helper function to recv n bytes or return None if EOF is hit
def recvall(sock, n):
    data = ''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

if __name__ == "__main__":
	print "... not an executable python module ..."
	sys.exit()