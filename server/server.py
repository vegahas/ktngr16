# -*- coding: utf-8 -*-
import SocketServer
import json
import time
import re

"""
Variables and functions that must be used by all the ClientHandler objects
must be written here (e.g. a dictionary for connected clients)
"""

currentUsers = dict()
help_msg = "login <username> - log in with the given username\nlogout           - log out\nmsg <message>    - send message\nnames            - list users in chat\nhelp             - view help text\n"
history = []


class ClientHandler(SocketServer.BaseRequestHandler):
    """
    This is the ClientHandler class. Everytime a new client connects to the
    server, a new ClientHandler object will be created. This class represents
    only connected clients, and not the server itself. If you want to write
    logic for the server, you must write it outside this class
    """
    username ='%'

    def encode(self,s,r,c):
        return json.dumps({'timestamp':time.ctime(time.time()), 'sender':s, 'response':r, 'content':c})

    def send(self,s,r,c):
        payload = self.encode(s,r,c)
        try:
            self.connection.send(payload)
        except:
            self.cancel()

    def recieve(self):
        try:
            package = self.connection.recv(4096)
            return package
        except:
            self.cancel()

    def cancel(self):
        self.logout(self.username)
        self.connection.close()
        print "Connection closed ..."


    def verifyUser(self, username):
        if username in currentUsers:
            return 2
        if re.match(r'[A-Za-z0-9]{1,}', username):
            return 1
        return False


    def login(self):
        self.send(HOST, "info", "Please login (type [help] for information) ...")
        while True:
            package = self.recieve()
            recmsg = json.loads(package)
            req = recmsg['request']
            if req == 'login':
                try:
                    username = recmsg['content']
                    y = self.verifyUser(username)
                    if y == 1:
                        c= 'Login successfull ...'
                        self.send(HOST,'info',c)
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
            self.send(HOST,r,c)

    def names(self):
        liste = currentUsers.keys()
        liste.sort()
        self.send(HOST,'info',liste)

    def sendMsg(self, msg, username):
        melding = self.encode(username,'message',msg)
        history.append(melding)
        for user in currentUsers:
            currentUsers[user].send(username,'message',msg)

    def logout(self,username):
        if username in currentUsers:
            del currentUsers[username]
        self.send(HOST,'info','Logout successfull ...')

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
            if not loggedin:
                self.username = self.login()
                loggedin = True
                currentUsers[self.username] = self
                self.send(HOST,'history',history)
            received_string = self.recieve()
            recmsg = json.loads(received_string)
            req = recmsg['request']
            if req == 'msg':
                self.sendMsg(recmsg['content'], self.username)
            elif req == 'logout':
                loggedin = False
                self.logout(self.username)
            elif req == 'help':
                self.send(HOST,'info',help_msg)
            elif req == 'names':
                self.names()
            else:
                self.send(HOST,'error','Invalid command, use [help] for info ...')





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
    HOST, PORT = '10.20.78.29', 9998
    print 'Server running...'

    # Set up and initiate the TCP server
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.serve_forever()



