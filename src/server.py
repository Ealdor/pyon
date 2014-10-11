# -*- coding: utf-8 -*-
#! /usr/bin/python

__author__="ealdor"
__date__ ="$27-sep-2014 10:10:18$"

import socket
import sys
import threading
import Queue
import random

import utils
import objects

global_queue = Queue.Queue() # cola FIFO para meter mensajes
connection_list = [] # lista que contiene tuplas con todas las conexiones de los clientes

class ClientThread(threading.Thread):
    def __init__(self, connection, client_address):
        threading.Thread.__init__(self)
        self.connection = connection
        self.address = client_address
        self.init()
        self.start()
    def init(self):
        utils.send_msg(self.connection, sv.map) # mandamos el mapa al cliente
        aux = objects.Object(random.randint(1, sv.map.width-2), random.randint(1, sv.map.height-2), '@') # creamos al jugador
        connection_list.append({"connection": self.connection, "address": self.address, "player": aux}) # añadimos al jugador a la lista
        for client in connection_list: # mandamos el jugador a todos y a nosotros todos los de la lista
            if client.get("address") != self.address:
                utils.send_msg(self.connection, {"type": "ADD", "player": client.get("player"), "address": client.get("address")})
            utils.send_msg(client.get("connection"), {"type": "ADD", "player": aux, "address": self.address})
    def run(self):
        global connection_list
        try:
            while True:
                self.data = utils.recv_msg(self.connection) # recibe datos del socket cliente
                if self.data:
                    if type(self.data) == type(""): # si recibimos un string
                        self.chat()
                    elif self.data.vk == 1: # el cliente pulsa ESC
                        self.pop()
                        break
                    elif self.data.vk in [14, 15, 16, 17]: # el cliente pulsa movimiento
                        self.move()
                else: # el cliente se ha desconectado (a lo bestia)
                    self.pop()
                    break
        except:
            print sys.exc_info()
        finally:
            global_queue.put({"type": "DELETE", "address": self.address})
            self.connection.close() # cerrar la conexión con el cliente
            sys.exit() # matamos el thread
    def chat(self): # función para mandar cosas del chat
        global_queue.put({"type": "CHAT", "chat": self.data, "address": self.address})
    def pop(self): # función para eliminar al cliente
        connection_list.pop(next(index for (index, d) in enumerate(connection_list) if d["address"] == self.address))
    def move(self): # función para mover al jugador
        for client in connection_list:
            if client.get("connection") == self.connection:
                if self.data.vk == 14: # arriba
                    client.get('player').move(0, -1, sv.map)
                elif self.data.vk == 15: # izquierda
                    client.get('player').move(-1, 0, sv.map)
                elif self.data.vk == 16: # derecha
                    client.get('player').move(1, 0, sv.map)
                elif self.data.vk == 17: # abajo
                    client.get('player').move(0, 1, sv.map)
                global_queue.put({"type": "UPDATE", "player": client.get("player"), "address": client.get("address")})
                break

# thread que procesa la cola global y manda los mensajes a todos los clientes (incluso al que lo ha generado)
class QueueThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()
    def run(self):
        global connection_list
        while True:
            data_queue = global_queue.get()
            for client in connection_list:
                try:
                    utils.send_msg(client.get("connection"), data_queue)
                    #[utils.send_msg(client.get("connection"), data_queue) for client in connection_list]
                except:
                    client.get("connection").close()

class Server():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) # crea un nuevo TCP/IP socket (familia, tipo y protocolo)
        self.server_address = ('localhost', 50215) # enlaza el socket a una dirección ((host, puerto)
        self.sock.bind(self.server_address)
        self.init_map()
    def init_map(self):
        self.map = objects.Map()
        self.map.make_map()   

if __name__ == "__main__":
    sv = Server()
    sv.sock.listen(1) # escuchar las conexiones realizadas al socket (máximo de conexiones en cola)
    QueueThread() # comenzamos a procesar la cola en un thread a parte
    try:
        while(True):
            connection, client_address = sv.sock.accept() # espera a recibir una conexión, devuelve (socket, dirección del cliente)
            ClientThread(connection, client_address) # se crea un thread por cada cliente
    except:
        print sys.exc_info()
    finally:
        server_running = False
        sv.sock.close()