# -*- coding: utf-8 -*-

__author__="ealdor"
__date__ ="$27-sep-2014 21:03:25$"

import sys
import textwrap
import string

import libtcod.libtcodpy as libtcod

# 8 - 850 x 560; 10 - 1060 x 700
FONT_SIZE = 10
ROOT_WIDTH = 1060/FONT_SIZE
ROOT_HEIGHT = 700/FONT_SIZE

# clase que representa un Tile
class Tile():
    def __init__(self, blocked):
        self.blocked = blocked # atributo que indica si el Tile bloquea el paso o no

# clase que representa un Mapa
class Map():
    def __init__(self):
        # tamaño de la consola game
        self.width = (70 * ROOT_WIDTH) / 100 # 80%
        self.height = (60 * ROOT_HEIGHT) / 100 # 60%
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
        libtcod.console_blit(self.console, 0, 0, ROOT_WIDTH, ROOT_HEIGHT, 0, 0, 0)

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
        libtcod.console_blit(map.console, 0, 0, ROOT_WIDTH, ROOT_HEIGHT, 0, 0, 0)
    def clear(self, map):
        libtcod.console_put_char(map.console, self.x, self.y, ' ', libtcod.BKGND_NONE) # limpiamos la posición anterior

# clase que representa el chat
class Chat():
    def __init__(self):
        self.width = (31 * ROOT_WIDTH) / 100 # 30%
        self.height = (60 * ROOT_HEIGHT) / 100 # 60%
        self.console = libtcod.console_new(self.width, self.height)
        self.enabled = False
        self.string = ""
        self.lines = []
        self.count = 0
    def draw_box(self):
        libtcod.console_print_frame(self.console , 0, 37, self.width, 5, True, libtcod.BKGND_DEFAULT, "ChatBox")
        aux = len(self.string)
        if aux < 30:
            libtcod.console_print_ex(self.console, 1, 38, libtcod.BKGND_NONE, libtcod.LEFT, self.string[0:30]+"_")
        elif aux == 30:
            libtcod.console_print_ex(self.console, 1, 38, libtcod.BKGND_NONE, libtcod.LEFT, self.string[0:30])
            libtcod.console_print_ex(self.console, 1, 39, libtcod.BKGND_NONE, libtcod.LEFT, "_")
        if aux > 30 and aux <60:
            libtcod.console_print_ex(self.console, 1, 38, libtcod.BKGND_NONE, libtcod.LEFT, self.string[0:30])
            libtcod.console_print_ex(self.console, 1, 39, libtcod.BKGND_NONE, libtcod.LEFT, self.string[30:60]+"_")
        if aux == 60:
            libtcod.console_print_ex(self.console, 1, 38, libtcod.BKGND_NONE, libtcod.LEFT, self.string[0:30])
            libtcod.console_print_ex(self.console, 1, 39, libtcod.BKGND_NONE, libtcod.LEFT, self.string[30:60])
            libtcod.console_print_ex(self.console, 1, 40, libtcod.BKGND_NONE, libtcod.LEFT, "_")
        if aux > 60 and aux < 90:
            libtcod.console_print_ex(self.console, 1, 38, libtcod.BKGND_NONE, libtcod.LEFT, self.string[0:30])
            libtcod.console_print_ex(self.console, 1, 39, libtcod.BKGND_NONE, libtcod.LEFT, self.string[30:60])
            libtcod.console_print_ex(self.console, 1, 40, libtcod.BKGND_NONE, libtcod.LEFT, self.string[60:90]+"_")
        if aux == 90:
            libtcod.console_print_ex(self.console, 1, 38, libtcod.BKGND_NONE, libtcod.LEFT, self.string[0:30])
            libtcod.console_print_ex(self.console, 1, 39, libtcod.BKGND_NONE, libtcod.LEFT, self.string[30:60])
            libtcod.console_print_ex(self.console, 1, 40, libtcod.BKGND_NONE, libtcod.LEFT, self.string[60:90])
        libtcod.console_blit(self.console, 0, 0, 0, 0, 0, ROOT_WIDTH-self.width, 0, 1.0, 1.0)
    def buffer(self, char):
        if len(self.string) <= 89:
            if char == 8: # borrar
                self.string = self.string[:-1]
            else:
                self.string += chr(char)
        else:
            if char == 8: # borrar
                self.string = self.string[:-1]
    def draw_lines(self):
        libtcod.console_print_frame(self.console , 0, 0, self.width, self.height-5, True, libtcod.BKGND_DEFAULT, "ChatLog")
        x = self.count
        for msg in self.lines:
            for line in textwrap.wrap(msg, 30):
                libtcod.console_print_ex(self.console, 1, 36-x, libtcod.BKGND_NONE, libtcod.LEFT, line)
                x -= 1
        libtcod.console_blit(self.console, 0, 0, 0, 0, 0, ROOT_WIDTH-self.width, 0, 1.0, 1.0)
    def update(self, s):
        self.count += len(textwrap.wrap(s, 30))
        if self.count > 38:
            self.count = 38
            del(self.lines[0])
        self.lines.append(s)
    def reset(self):
        self.enabled = False
        self.string = ""

class MainScreenOption():
    def __init__(self, active, name, posx, posy, console, message, maxlen):
        self.active = active
        self.maxlen = maxlen
        self.name = name
        self.posx = posx
        self.posy = posy
        self.message = message
        self.console = console
        self.content = ""
    def draw(self, color):
        libtcod.console_set_default_foreground(self.console, color)
        libtcod.console_print_frame(self.console, self.posx, self.posy, 35, 5, True, libtcod.BKGND_NONE, 0)
        libtcod.console_print_ex(self.console, self.posx+2, self.posy, libtcod.BKGND_NONE, libtcod.LEFT, self.name)
        libtcod.console_print_ex(self.console, self.posx+36, self.posy+2, libtcod.BKGND_NONE, libtcod.LEFT, self.message)
        libtcod.console_print_ex(self.console, self.posx+1, self.posy+2, libtcod.BKGND_NONE, libtcod.LEFT, self.content)

class MainScreen():
    def __init__(self):
        self.width = ROOT_WIDTH
        self.height = ROOT_HEIGHT
        self.console = libtcod.console_new(self.width, self.height)
        libtcod.console_set_default_background(self.console, libtcod.black)
        libtcod.console_set_default_foreground(self.console, libtcod.lighter_grey)
        libtcod.console_set_alignment(self.console, libtcod.LEFT)
        self.active = True
        self.options = [MainScreenOption(True, " Name ", 5, 22, self.console, "(max length: 5)", 10), \
                        MainScreenOption(False, " Server ", 5, 29, self.console, "(IP:PORT format)", 25)]
    def handle_keys(self):
        key = libtcod.console_check_for_keypress()
        if key.vk == libtcod.KEY_ESCAPE:    
            return 0
        elif key.vk == libtcod.KEY_TAB:
            self.switch()
        elif key.vk == libtcod.KEY_ENTER:
            self.check()
            return 1
        elif key.c != 0:
            self.process(key.c)
    def draw(self):
        libtcod.console_set_default_foreground(self.console, libtcod.azure)
        libtcod.console_print_ex(self.console, self.width/2, 5, libtcod.BKGND_NONE, libtcod.CENTER, "P Y O N")
        libtcod.console_set_default_foreground(self.console, libtcod.light_blue)
        libtcod.console_print_ex(self.console, self.width/2, 8, libtcod.BKGND_NONE, libtcod.CENTER, "An online Roguelike about dre@ms")
        for option in self.options:
            if option.active:
                option.draw(libtcod.red)
            else:
                option.draw(libtcod.lighter_grey)
        libtcod.console_set_default_foreground(self.console, libtcod.lighter_grey)
        libtcod.console_hline(self.console, 0, 13, self.width, libtcod.BKGND_NONE)
        libtcod.console_print_ex(self.console, self.width/2, 17, libtcod.BKGND_NONE, libtcod.CENTER, "'Tab' to switch; 'Enter' to connect; 'Esc' to exit")
        libtcod.console_print(self.console, 1, self.height-2, "alpha 071014 (by ealdor) - Powered by libtcod")
    
        libtcod.console_blit(self.console, 0, 0, 0, 0, 0, 0, 0, 1.0, 1.0)
    def switch(self):
        index = [self.options.index(option) for option in self.options if option.active][0]
        self.options[index].active = False
        if index == len(self.options)-1:
            self.options[0].active = True
        else:
            self.options[index+1].active = True
    def check(self):
        self.active = False
        libtcod.console_clear(self.console)
        libtcod.console_blit(self.console, 0, 0, 0, 0, 0, 0, 0, 1.0, 1.0)
        self.data = string.split(self.options[1].content, ":")

    def process(self, char):
        for option in self.options:
            if option.active:
                if char == 8: # borrar
                    option.content = option.content[:-1]
                else:
                    if len(option.content) < option.maxlen:
                            option.content += chr(char)
                break

if __name__ == "__main__":
    print "... not an executable module ..."
    sys.exit()
