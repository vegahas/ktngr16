# -*- coding: utf-8 -*-
import SocketServer
import json
import time

"""
Variables and functions that must be used by all the ClientHandler objects
must be written here (e.g. a dictionary for connected clients)
"""
currentUsers = dict()
help_msg = "hei"
history = []


class ClientHandler(SocketServer.BaseRequestHandler):
    """
    This is the ClientHandler class. Everytime a new client connects to the
    server, a new ClientHandler object will be created. This class represents
    only connected clients, and not the server itself. If you want to write
    logic for the server, you must write it outside this class
    """

    def encode(self, s, r, c):
        return json.loads({'timestamp':time.ctime(time.time()), 'sender':s, 'response':r, 'content':c})

    def verifyUser(self, username):
        return False

    def login(self):
        respons = self.encode(HOST, "info", "Please login (type [help] for information) ...")
        self.connection.send(respons)
        while True:
            a = self.connection.recv(4096)
            recmsg = json.dumps(a)
            req = recmsg['request']
            if req.startswith('login '):
                try:
                    username = recmsg['content']
                    y = self.verifyUser(username)
                    if y == 1:
                        c= 'Login successfull ...'
                        self.connection.send(self.encode(HOST,'info',c))
                        return username
                    elif y == 2:
                        c = 'Username taken ...'
                    else:
                        c= 'Invalid username, use alphanumerical characters ...'
                    r = 'error'
                except:
                    c = 'Invalid syntax ...'
                    r = 'error'
            elif req == 'help':
                c = help_msg
                r = 'info'
            else:
                c = "Invalid command ..."
                r = 'error'
            self.connection.send(self.encode(HOST,r,c))

    def names(self):
        liste = currentUsers.keys().sort()
        self.connection.send(self.encode(HOST,'info',liste))

    def sendMsg(self, msg, username):
        melding = self.encode(username,'message',msg)
        history.append(melding)
        for user in currentUsers:
            currentUsers[user].send(melding)



    def handle(self):
        """
        This method handles the connection between a client and the server.
        """
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request
        loggedin = False
        username = ''

        # Loop that listens for messages from the client
        while True:
            if not loggedin:
                username = self.login()
                loggedin = True
                currentUsers[username] = self
                self.connection.send(self.encode(HOST,'history',history))
            received_string = self.connection.recv(4096)
            recmsg = json.dumps(received_string)
            req = recmsg['request']
            if req.startswith('msg '):
                self.sendMsg(recmsg['Content'], username)
            elif req == 'logout':
                loggedin = False
                del currentUsers[username]
                self.connection.send(self.encode(HOST,'info','Logout successfull ...'))
            elif req == 'help':
                self.connection.send(self.encode(HOST,'info',help_msg))
            elif req == 'names':
                self.names()
            else:
                self.connection.send(self.encode(HOST,'error','Invalid command, use [help] for info ...'))





            # TODO: Add handling of received payload from client


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """
    This class is present so that each client connected will be ran as a own
    thread. In that way, all clients will be served by the server.

    No alterations are necessary
    """
    allow_reuse_address = True

if __name__ == "__main__":
    """
    This is the main method and is executed when you type "python Server.py"
    in your terminal.

    No alterations are necessary
    """
    HOST, PORT = 'localhost', 9998
    print 'Server running...'

    # Set up and initiate the TCP server
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.serve_forever()



