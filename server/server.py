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
        while True:
            recmsg = json.dumps(self.connection.recv(4096))
            melding = recmsg['request']
            if melding.startswith('login '):
                try:
                    x = melding.split(' ')
                    username = x[1]
                    if self.verifyUser(username):
                        c= 'You are now logged in ...'
                        self.connection.send(self.encode(HOST,'info',c))
                        return username
                    else:
                        c= 'Invalid username, use alphanumerical characters ...'
                        r = 'error'
                except:
                    c = 'Invalid syntax ...'
                    r = 'error'
            elif melding.startswith('help'):
                c = help_msg
                r = 'info'
            else:
                c = "Invalid command ..."
                r = 'error'
            self.connection.send(self.encode(HOST,r,c))

    def handle(self):
        """
        This method handles the connection between a client and the server.
        """
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request
        loggedin = False

        # Loop that listens for messages from the client
        while True:
            received_string = self.connection.recv(4096)
            if not loggedin:
                username = self.login()
                loggedin = True
                currentUsers[username] = (self.ip, self.port)




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



