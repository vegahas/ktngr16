# -*- coding: utf-8 -*-
import SocketServer
import json
import time

"""
Variables and functions that must be used by all the ClientHandler objects
must be written here (e.g. a dictionary for connected clients)
"""

main_room = 'lobby'
admin = dict()
currentUsers = dict()
muted = dict()
banned = dict()
mods = dict()
rooms = {main_room: dict(),
         'sofa': dict(),
         'school': dict()}
help_msg = "\nList of commands\n" \
           "login <username> - log in with the given username\n" \
           "logout           - log out\n" \
           "msg <message>    - send message\n" \
           "pm <user> <msg>  - send private message to user\n" \
           "names            - list users in chat\n" \
           "room <name>      - change to chosen room\n" \
           "rooms            - list all rooms\n" \
           "help             - view help text\n"
history = {main_room: [],
           'moderators': [],
           'sofa': [],
           'school': []}
mod_msg = "\nList of moderator commands\n" \
          "mod mods\n" \
          "mod users            - list all users\n" \
          "mod mute <user>      - mute user\n" \
          "mod un_mute <user>   - un-mute user\n" \
          "mod muted            - list muted users\n" \
          "mod kick <user>      - kick user\n" \
          "mod ban <user>       - ban user\n" \
          "mod un_ban <user>    - un-ban user\n" \
          "mod banned           - list banned users" \
          "mod new_room <name>  - create new chat room\n" \
          "mod del_room <room>  - delete a chat room\n"
adm_msg = "\nList of administrator commands\n" \
          "adm add <username>   - make user a moderator\n" \
          "adm del <username>   - remove a moderator\n"


class ClientHandler(SocketServer.BaseRequestHandler):
    """
    This is the ClientHandler class. Everytime a new client connects to the
    server, a new ClientHandler object will be created. This class represents
    only connected clients, and not the server itself. If you want to write
    logic for the server, you must write it outside this class
    """
    username = '%'
    current_room = main_room

    def encode(self, s, r, c):
        return json.dumps({'timestamp': time.ctime(time.time()), 'sender': s, 'response': r, 'content': c})

    def send(self, s, r, c):
        payload = self.encode(s, r, c)
        try:
            self.connection.send(payload)
        except:
            self.cancel()

    def receive(self):
        try:
            package = self.connection.recv(4096)
            return json.loads(package)
        except:
            self.cancel()

    def cancel(self):
        self.remove()
        self.connection.close()
        print "Connection closed ..."

    def remove(self):
        if self.username in currentUsers:
            del currentUsers[self.username]
        if self.username in mods:
            del mods[self.username]
        if self.username in rooms[self.current_room]:
            del rooms[self.current_room][self.username]
        if self.username in admin:
            del admin[self.username]

    def verify_user(self, username):
        if (username in currentUsers) or (username in rooms):
            return 2
        if len(username) > 10:
            return 3
        if username.isalnum():
            return 1
        return False

    def initialize(self, username):
        c = 'Login successful ...\nYour are in: ' + self.current_room
        self.username = username
        self.send(HOST, 'info', c)
        currentUsers[self.username] = self
        rooms[self.current_room][self.username] = self

    def handle_adm(self, content):
        if (content == 'accept') and (not bool(admin)):
            if not bool(mods):
                admin[self.username] = None
                mods[self.username] = None
                return 'Success'
            elif self.username in mods:
                admin[self.username] = None
                return 'Success'
        elif self.username in admin:
            if content == 'help':
                self.send(HOST, 'info', adm_msg)
                return 'Success'
            else:
                try:
                    x = content.split(' ', 1)
                    cmd = x[0]
                    usr = x[1]
                except:
                    return 'Fail'
                if (cmd == 'add') and (usr in currentUsers) and (usr not in mods):
                    mods[usr] = None
                    currentUsers[usr].send(HOST, 'info', 'You are now a moderator. Type [mod help] for commands ...')
                    return 'Success'
                elif (cmd == 'del') and (usr in currentUsers) and (usr in mods) and (usr != self.username):
                    del mods[usr]
                    currentUsers[usr].send(HOST, 'info', 'You are no longer a moderator ...')
                    return 'Success'
        return 'Fail'

    def handle_login(self):
        self.send(HOST, "info", "Please login (type [help] for information) ...")
        while True:
            package = self.receive()
            req = package['request']
            if req == 'login':
                try:
                    username = package['content']
                    y = self.verify_user(username)
                    if y == 1:
                        self.initialize(username)
                        break
                    elif y == 2:
                        c = 'Username taken ...'
                    elif y == 3:
                        c = 'Username too long, max 10 characters ...'
                    else:
                        c = 'Invalid username, use alphanumerical characters ...'
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
            self.send(HOST, r, c)
        self.send(HOST, 'history', history[self.current_room])

    def handle_rooms(self):
        x = '\nRoom\tUsers\n'
        i = rooms.keys()
        i.sort()
        for j in i:
            y = self.handle_list(rooms[j])
            x += j + '\t' + y + '\n'
        self.send(HOST, 'info', x)

    def handle_list(self, dictionary):
        x = dictionary.keys()
        x.sort()
        a = ''
        for element in x:
            a += element + ', '
        return a[0:len(a)-2]

    def handle_pm(self, content):
        try:
            x = content.split(' ', 1)
            usr = x[0]
            if usr in currentUsers:
                currentUsers[usr].send(self.username, 'message', 'Private message: ' + x[1])
                self.send(self.username, 'message', 'Pm to ' + usr + ' : ' + x[1])
            else:
                self.send(HOST, 'error', 'User not online ...')
        except:
            self.send(HOST, 'error', 'Invalid syntax. Correct: [pm <username> <message>] ...')

    def handle_room(self, content):
        if content in rooms:
            if self.username not in rooms[content]:
                rooms[content][self.username] = self
                del rooms[self.current_room][self.username]
                self.send(HOST, 'history', history[content])
            self.current_room = content
            c = 'Your are in: ' + content
        else:
            c = 'Invalid room ...'
        self.send(HOST, 'info', c)

    def handle_mod(self, content):
        if self.username in mods:
            if content == 'help':
                return mod_msg
            elif content == 'muted':
                return 'Muted: ' + self.handle_list(muted)
            elif content == 'banned':
                return 'Banned: ' + self.handle_list(banned)
            elif content == 'mods':
                return 'Moderators: ' + self.handle_list(mods)
            elif content == 'users':
                return 'Online users: ' + self.handle_list(currentUsers)
            try:
                x = content.split(' ', 1)
                cmd = x[0]
                usr = x[1]
            except:
                return 'Fail'
            if cmd == 'un_ban':
                if usr in banned:
                    del banned[usr]
                    return 'Success'
            elif (cmd == 'new_room') and (self.verify_user(usr) == 1):
                rooms[usr] = dict()
                history[usr] = []
                return 'Success'
            elif cmd == 'del_room':
                if (usr in rooms) and (usr != main_room):
                    for i in rooms[usr]:
                        a = currentUsers[i]
                        rooms[main_room][i] = a
                        a.current_room = main_room
                        a.send(HOST, 'info', 'Room deleted, you are in: ' + a.current_room)
                    del rooms[usr]
                    del history[usr]
                    return 'Success'
            elif (usr not in mods) and (usr in currentUsers):
                if cmd == 'kick':
                    currentUsers[usr].send(HOST, 'info', 'You have been kicked!')
                    currentUsers[usr].handle_logout()
                    return 'Success'
                elif cmd == 'mute':
                    if usr not in muted:
                        muted[usr] = None
                        return 'Success'
                elif cmd == 'un_mute':
                    if usr in muted:
                        del muted[usr]
                        return 'Success'
                elif cmd == 'ban':
                    banned[usr] = currentUsers[usr].ip
                    currentUsers[usr].send(HOST, 'info', 'You have been banned!')
                    currentUsers[usr].cancel()
                    return 'Success'
        return 'Fail'

    def handle_msg(self, msg):
        if self.username not in muted:
            melding = self.encode(self.username, 'message', msg)
            history[self.current_room].append(melding)
            for user in rooms[self.current_room]:
                currentUsers[user].send(self.username, 'message', msg)
        else:
            self.send(HOST, 'error', 'You are muted! ...')

    def handle_logout(self):
        self.remove()
        self.send(HOST, 'info', 'Logout successful ...')
        self.handle_login()

    def handle(self):
        """
        This method handles the connection between a client and the server.
        """
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request
        if self.ip in banned.values():
            self.cancel()
        self.handle_login()
        while True:
            package = self.receive()
            req = package['request']
            if req == 'msg':
                self.handle_msg(package['content'])
            elif req == 'logout':
                self.handle_logout()
            elif req == 'help':
                self.send(HOST, 'info', help_msg)
            elif req == 'names':
                self.send(HOST, 'info', 'Users in ' + self.current_room + ': ' + self.handle_list(rooms[self.current_room]))
            elif req == 'mod':
                self.send(HOST, 'info', self.handle_mod(package['content']))
            elif req == 'room':
                self.handle_room(package['content'])
            elif req == 'rooms':
                self.handle_rooms()
            elif req == 'adm':
                self.send(HOST, 'info', self.handle_adm(package['content']))
            elif req == 'pm':
                self.handle_pm(package['content'])
            else:
                self.send(HOST, 'error', 'Invalid command, use [help] for info ...')


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
