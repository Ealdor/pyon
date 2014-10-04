# -*- coding: utf-8 -*-
#! /usr/bin/python

__author__="ealdor"
__date__ ="$27-sep-2014 10:09:37$"

import socket
import sys
import threading
import libtcod.libtcodpy as libtcod
import select

import server_utils

client_running = True

connection_list_lock = threading.Lock() # variable para controlar el acceso a connection_list
connection_list = []
        
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
                    data = server_utils.recv_msg(self.s) # recibimos mensaje del servidor
                    if data:
                        process_data(data)
                    else: # el servidor devuelve None cuando se desconecta
                        break
                    self.server_response = True
        except:
            print sys.exc_info()
        finally:
            self.s.close() # cerramos el socket
            sys.exit()

# funcion para procesar mensajes del servidor
def process_data(data):
    type = data.get("type")
    if type == "CHAT": # si es un mensaje de chat
        clientChat.update(data.get("chat"))
    else:
        connection_list_lock.acquire()
        if type == "ADD": # si es un mensaje de cliente nuevo conectado
            connection_list.append({"address": data.get("address"), "player": data.get("player")})
        elif type == "UPDATE": # si es un mensaje de actualizacion de cliente (solo movimiento de momento)
            for client in connection_list:
                if client.get("address") == data.get("address"):
                    client["player"] = data.get("player")
        elif type == "DELETE":  # si es un mensaje de desconexión de un cliente
            connection_list.pop(next(index for (index, d) in enumerate(connection_list) if d["address"] == data.get("address")))
        connection_list_lock.release()
    return

# función que inicializa libtcod y se conecta al servidor
def init_client(arg):
    server_utils.init_libtcod() # inicializamos libtcod
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) # crea un nuevo TCP/IP socket (familia, tipo y protocolo)
    server_address = (arg[1], int(arg[2])) # conectarse a un socket remoto ((host, puerto) 127.0.0.1:50215
    try:
        sock.connect(server_address)
    except:
        print sys.exc_info()
    return sock

# función que recibe el mapa del servidor
def init_map():
    map = server_utils.recv_msg(clientSock)
    map.console = libtcod.console_new(map.width, map.height)
    return map

# función que inicializa el chat
def init_chat():
    chat = server_utils.Chat()
    return chat

# función para controlar la pulsación de teclas
def handle_keys():
    if s.server_response: # si el servidor ya nos ha respondido
        key = libtcod.console_check_for_keypress() # esperamos la pulsación
        if not clientChat.enabled: # si el chat no esta en marcha
            if key.vk == libtcod.KEY_ESCAPE: # salimos del juego
                server_utils.send_msg(clientSock, key)
                s.server_response = False
                return True
            elif key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_RIGHT:
                s.server_response = False
            elif key.c == 99: # si se ha pulsado la 'c'
                clientChat.enabled = True # habilitamos el chat
                return False
            server_utils.send_msg(clientSock, key) # mandamos la pulsación
        else: # si el chat está habilitado
            if key.vk == libtcod.KEY_ENTER: # mandamos la cadena si no está vacía
                if clientChat.string != "":
                    server_utils.send_msg(clientSock, clientChat.string)
                    s.server_response = False
                clientChat.reset()
            elif key.c != 0: # escribimos en el chatbox
                clientChat.buffer(key.c)
    return False

# función para dibujar y borrar
def draw_all():
    clientMap.draw_map() # dibujamos el mapa
    connection_list_lock.acquire()
    for client in connection_list: # dibujamos los clientes
        player = client.get('player')
        player.draw(clientMap)
    for client in connection_list: # limpiamos los clientes
        player = client.get('player')
        player.clear(clientMap)
    connection_list_lock.release()
    if clientChat.enabled:
        clientChat.draw_box() # dibujamos el chatbox
    clientChat.draw_lines() # dibujamos las lineas del chat
    libtcod.console_clear(clientChat.console) # borramos el chat entero

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Use: python py@on_client.py SERVER_IP SERVER_PORT"
        sys.exit()
    clientSock = init_client(sys.argv)
    clientMap = init_map()
    clientChat = init_chat()
    s = ServerThread(clientSock) # creamos el thread del cliente para empezar a recibir
    while(True):
        draw_all()
        libtcod.console_flush() # actualizamos la pantalla
        exit = handle_keys()
        if exit:
            break
    client_running = False
    sys.exit()