# -*- coding: utf-8 -*-

__author__="ealdor"
__date__ ="$27-sep-2014 10:09:37$"

import socket
import sys
import threading
import select

import libtcod.libtcodpy as libtcod
import utils
import objects

client_running = True

connection_list_lock = threading.Lock() # variable para controlar el acceso a connection_list
connection_list = []

global_clientChat = None
        
# clase serverThread recibe mensajes del servidor al que se conecta
class ServerThread(threading.Thread):
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.s = sock
        self.s.setblocking(0) # socket no bloqueante
        self.server_response = True # variable para saber cuando ha respondido el servidor
        self.start()
    def run(self):
        try:
            while True:
                if not client_running: # el cliente ha salido y hay que matar el thread
                    break
                ready = select.select([self.s], [], [], 5) # timeout de 5 segundos por si el cliente cierra (a lo bestia)
                if ready[0]:
                    self.data = utils.recv_msg(self.s) # recibimos mensaje del servidor
                    if self.data:
                        self.process_data()
                    else: # el servidor devuelve None cuando se desconecta
                        break
                    self.server_response = True
        except:
            print sys.exc_info()
        finally:
            self.s.close() # cerramos el socket
            sys.exit()
    def process_data(self):
        data_type = self.data.get("type")
        if data_type == "CHAT": # si es un mensaje de chat
            global_clientChat.update(self.data.get("chat"))
        else:
            connection_list_lock.acquire()
            if data_type == "ADD": # si es un mensaje de cliente nuevo conectado
                connection_list.append({"address": self.data.get("address"), "player": self.data.get("player")})
            elif data_type == 'UPDATE': # si es un mensaje de actualizacion de cliente (solo movimiento de momento)
                for client in connection_list:
                    if client.get("address") == self.data.get("address"):
                        client["player"] = self.data.get("player")
                        break
            elif data_type == "DELETE":  # si es un mensaje de desconexión de un cliente
                connection_list.pop(next(index for (index, d) in enumerate(connection_list) if d["address"] == self.data.get("address")))
            connection_list_lock.release()
        return

class Client():
    def __init__(self, add):
        self.init_client(add)
        self.init_map()
        self.init_chat(add)
        self.st = ServerThread(self.clientSock) # creamos el thread del cliente para empezar a recibir
    def init_client(self, add):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) # crea un nuevo TCP/IP socket (familia, tipo y protocolo)
        server_address = (add[0][0], int(add[0][1])) # conectarse a un socket remoto ((host, puerto) 127.0.0.1:50215
        try:
            sock.connect(server_address)
        except:
            print sys.exc_info()
            sys.exit()
        self.clientSock = sock
    def init_map(self):
        self.clientMap = utils.recv_msg(self.clientSock)
        self.clientMap.console = libtcod.console_new(self.clientMap.width, self.clientMap.height)
    def init_chat(self, add):
        global global_clientChat
        self.clientChat = objects.Chat(add[1])
        global_clientChat = self.clientChat
    def draw(self):
        global connection_list
        self.clientMap.draw_map() # dibujamos el mapa
        connection_list_lock.acquire()
        [client.get('player').draw(self.clientMap) for client in connection_list] # dibujamos los clientes
        [client.get('player').clear(self.clientMap) for client in connection_list] # limpiamos los clientes
        connection_list_lock.release()
        if self.clientChat.enabled:
            self.clientChat.draw_box() # dibujamos el chatbox
        self.clientChat.draw_lines() # dibujamos las lineas del chat
        libtcod.console_clear(self.clientChat.console) # borramos el chat entero
    def handle_keys(self):
        if self.st.server_response: # si el servidor ya nos ha respondido
            key = libtcod.console_check_for_keypress() # esperamos la pulsación
            if not self.clientChat.enabled: # si el chat no esta en marcha
                if key.vk == libtcod.KEY_ESCAPE: # salimos del juego
                    utils.send_msg(self.clientSock, key)
                    self.st.server_response = False
                    return 0
                elif key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_RIGHT:
                    self.st.server_response = False
                elif key.c == 99: # si se ha pulsado la 'c'
                    self.clientChat.enabled = True # habilitamos el chat
                utils.send_msg(self.clientSock, key) # mandamos la pulsación
            else: # si el chat está habilitado
                if key.vk == libtcod.KEY_ENTER: # mandamos la cadena si no está vacía
                    if self.clientChat.string != "":
                        utils.send_msg(self.clientSock, self.clientChat.name+self.clientChat.string)
                        self.st.server_response = False
                    self.clientChat.reset()
                elif key.c != 0: # escribimos en el chatbox
                    self.clientChat.buffer(key.c)
        return 2