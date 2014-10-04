# -*- coding: utf-8 -*-
#! /usr/bin/python

__author__="ealdor"
__date__ ="$27-sep-2014 10:10:18$"

import socket
import sys
import threading
import Queue
import random

import server_utils

global_queue = Queue.Queue() # cola FIFO para meter mensajes
connection_list = [] # lista que contiene tuplas con todas las conexiones de los clientes
server_running = True

class ClientThread(threading.Thread):
    def __init__(self, connection, client_address):
        threading.Thread.__init__(self)
        self.connection = connection
        self.address = client_address
        self.init()
        self.start()
    def init(self):
        server_utils.send_msg(self.connection, serverMap) # mandamos el mapa al cliente
        aux = server_utils.Object(random.randint(1, serverMap.width-2), random.randint(1, serverMap.height-2), '@') # creamos al jugador
        connection_list.append({"connection": self.connection, "address": self.address, "player": aux}) # añadimos al jugador a la lista
        for client in connection_list: # mandamos el jugador a todos y a nosotros todos los de la lista
            server_utils.send_msg(self.connection, {"type": "ADD", "player": client.get("player"), "address": client.get("address")})
            server_utils.send_msg(client.get("connection"), {"type": "ADD", "player": aux, "address": self.address})
    def run(self):
        global connection_list
        try:
            while True:
                data = server_utils.recv_msg(self.connection) # recibe datos del socket cliente
                if data:
                    if type(data) == type(""): # si recibimos un string
                        chat(data, self.address)
                    elif data.vk == 1: # el cliente pulsa ESC
                        pop(self.address)
                        break
                    elif data.vk in [14, 15, 16, 17]: # el cliente pulsa movimiento
                        move(self.connection, data)
                else: # el cliente se ha desconectado (a lo bestia)
                    pop(self.address)
                    break
        except:
            print sys.exc_info()
        finally:
            global_queue.put({"type": "DELETE", "address": self.address})
            self.connection.close() # cerrar la conexión con el cliente
            sys.exit() # matamos el thread

# función para mandar cosas del chat
def chat(data, address):
    global_queue.put({"type": "CHAT", "chat": data, "address": address})

# función para eliminar al cliente
def pop(address):
    global connection_list
    connection_list.pop(next(index for (index, d) in enumerate(connection_list) if d["address"] == address))

# función para mover al jugador
def move(connection, data):
    global connection_list
    for client in connection_list:
        if client.get("connection") == connection:
            if data.vk == 14: # arriba
                client.get('player').move(0, -1, serverMap)
            elif data.vk == 15: # izquierda
                client.get('player').move(-1, 0, serverMap)
            elif data.vk == 16: # derecha
                client.get('player').move(1, 0, serverMap)
            elif data.vk == 17: # abajo
                client.get('player').move(0, 1, serverMap)
            global_queue.put({"type": "UPDATE", "player": client.get("player"), "address": client.get("address")})
            break
    return

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
                server_utils.send_msg(client.get("connection"), data_queue)

# función que inicializa el servidor
def init_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) # crea un nuevo TCP/IP socket (familia, tipo y protocolo)
    server_address = ('localhost', 50215) # enlaza el socket a una dirección ((host, puerto)
    sock.bind(server_address)
    return sock

# creamos un mapa y lo rellenamos
def init_map():
    m = server_utils.Map()
    m.make_map()
    return m

if __name__ == "__main__":
    serverSock = init_server()
    serverMap = init_map()
    serverSock.listen(1) # escuchar las conexiones realizadas al socket (máximo de conexiones en cola)
    QueueThread() # comenzamos a procesar la cola en un thread a parte
    try:
        while(True):
            connection, client_address = serverSock.accept() # espera a recibir una conexión, devuelve (socket, dirección del cliente)
            ClientThread(connection, client_address) # se crea un thread por cada cliente
    except:
        print sys.exc_info()
    finally:
        server_running = False
        serverSock.close()