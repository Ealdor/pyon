# -*- coding: utf-8 -*-
#! /usr/bin/python

__author__="ealdor"
__date__ ="$27-sep-2014 21:03:25$"

import libtcodpy as libtcod
import sys
import struct
import cPickle as pickle
import textwrap

# tamaño de la consola root
SCREEN_WIDTH = 130
SCREEN_HEIGHT = 45

# clase que representa un Tile
class Tile():
    def __init__(self, blocked):
        self.blocked = blocked # atributo que indica si el Tile bloquea el paso o no

# clase que representa un Mapa
class Map():
    def __init__(self):
        # tamaño de la consola game
        self.width = 80
        self.height = 45
        self.tiles = None
        # color de las paredes y el suelo
        self.color_dark_wall = libtcod.Color(0, 0, 100)
        self.color_dark_ground = libtcod.Color(50, 50, 150)
        
    def make_map(self):
        self.tiles = [[ Tile(False) # rellenamos el mapa game Tiles sin bloquear
            for y in range(self.height) ]
                for x in range(self.width) ]    
        # ponemos los Tiles bloqueantes
        self.tiles[30][22].blocked = True
        self.tiles[50][22].blocked = True
        for y in range(self.height):
            self.tiles[0][y].blocked = True
            self.tiles[self.width-1][y].blocked = True
        for x in range(self.width):
            self.tiles[x][0].blocked = True
            self.tiles[x][self.height-1].blocked = True
    def draw_map(self):
        for y in range(self.height): # dibujamos la consola del juego (game)
            for x in range(self.width):
                wall = self.tiles[x][y].blocked
                if wall:
                    libtcod.console_set_char_background(self.console, x, y, self.color_dark_wall, libtcod.BKGND_SET)
                else:
                    libtcod.console_set_char_background(self.console, x, y, self.color_dark_ground, libtcod.BKGND_SET)
        libtcod.console_blit(self.console, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

# clase que representa un Objeto (de momento solo un jugador)
class Object():
    def __init__(self, x, y, char, color=libtcod.white):
        # atributos de posición
        self.x = x
        self.y = y
        # carácter que representa al objeto y color
        self.char = char
        self.color = color
    def move(self, dx, dy, map):
        if not map.tiles[self.x + dx][self.y + dy].blocked: # movemos al jugador si la nueva posición no esta bloqueada
            self.x += dx
            self.y += dy
    def draw(self, map):
        # seteamos el color de fondo y dibujamos el caracter en su posición
        libtcod.console_set_default_foreground(map.console, self.color)
        libtcod.console_put_char(map.console, self.x, self.y, self.char, libtcod.BKGND_NONE)
        libtcod.console_blit(map.console, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
    def clear(self, map):
        libtcod.console_put_char(map.console, self.x, self.y, ' ', libtcod.BKGND_NONE) # limpiamos la posición anterior

# clase que representa el chat
class Chat():
    def __init__(self):
        self.width = 50
        self.height = 45
        self.console = libtcod.console_new(self.width, self.height)
        self.enabled = False
        self.string = ""
        self.underscore = [1, 41]
        self.lines = []
        self.count = 0
    def draw_box(self):
        libtcod.console_print_frame(self.console , 0, 40, 50, 5, True, libtcod.BKGND_DEFAULT)
        libtcod.console_print_ex(self.console, 2, 40, libtcod.BKGND_NONE, libtcod.LEFT, "ChatBox")
        libtcod.console_print_ex(self.console, 1, 41, libtcod.BKGND_NONE, libtcod.LEFT, self.string[0:48])
        libtcod.console_print_ex(self.console, 1, 42, libtcod.BKGND_NONE, libtcod.LEFT, self.string[48:96])
        libtcod.console_print_ex(self.console, 1, 43, libtcod.BKGND_NONE, libtcod.LEFT, self.string[96:144])
        if self.underscore[0] > 48 and self.underscore[0] < 96:
            if self.underscore[1] == 42:
                self.underscore[0] = 1
                self.underscore[1] = 43
            else:
                self.underscore[0] = 1
                self.underscore[1] = 42
        if len(self.string) <= 143:
            libtcod.console_print_ex(self.console, self.underscore[0], self.underscore[1], libtcod.BKGND_NONE, libtcod.LEFT, "_")
        libtcod.console_blit(self.console, 0, 0, 0, 0, 0, 80, 0)
    def buffer(self, char):
        if len(self.string) <= 143:
            if char == 8: # borrar
                self.string = self.string[:-1]
                if self.underscore[0] > 1:
                    self.underscore[0] -= 1
            else:
                self.string += chr(char)
                self.underscore[0] += 1
    def draw_lines(self):
        libtcod.console_print_frame(self.console , 0, 0, 50, 40, True, libtcod.BKGND_DEFAULT)
        libtcod.console_print_ex(self.console, 2, 0, libtcod.BKGND_NONE, libtcod.LEFT, "ChatLog")
        x = self.count
        for msg in self.lines:
            for line in textwrap.wrap(msg, 48):
                libtcod.console_print_ex(self.console, 1, 39-x, libtcod.BKGND_NONE, libtcod.LEFT, line)
                x -= 1
        libtcod.console_blit(self.console, 0, 0, 0, 0, 0, 80, 0)
    def update(self, s):
        self.count += len(textwrap.wrap(s, 48))
        if self.count > 38:
            self.count = 38
            del(self.lines[0])
        self.lines.append(s)
    def reset(self):
        self.enabled = False
        self.string = ""
        self.underscore[0] = 1
        self.underscore[1] = 41

# creamos la ventana; consola principal
def init_libtcod():
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'py@on', False)

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
    print "... not an executable module ..."
    sys.exit()
