"""
Priority:
TODO: locations folder. xml files for (probably) individual zones

TODO: Attempting to connect ... 3.. 2.. 1.. (for loop in range(TIMEOUT))
TODO: Allow connect only at appropriate times

TODO: Store recent user commands to recall
TODO: When command goes through, stored to list. A key press will put those inputs into input entry

TODO: the color tag checker is reviewing all text each time text is displayed. It is changing previous tags (I think the order is based tag declaration order) and redoing all previous work each time. Have it just look at text being posted, possibly before insertion?
TODO: Special text reading system, to break large strings into multiple display_text_outputs.

TODO: Get listen to broadcasts to end smoothly

TODO: Serializing of color codes, to allow user to set and save client text color preferences

ISSUES

"""

import tkinter as tk
import actions
import socket
import datetime
import threading
import pickle

from ui import *

HEADER_LENGTH = 10
VERB_HEADER_LENGTH = 10

PORT = 4400
TIMEOUT = 3

BOUND_KEYS = ['<Return>']

FCODES = {'TITLE': 'location_dsc', 'PHYSD': 'default', 'ITEMS': 'items_dsc', 'DENZS': 'denizens_dsc', 'EXITS': 'exits_dsc'}


class Client(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(TIMEOUT)

        self.title('Hearthfire')
        self.geometry('1500x800')
        self.config(background='black')

        self.game_screen = GameScreen(self)
        self.game_screen.pack(fill='both')

        self.game_screen.player_input.focus_force()
        self.connect_prompt()

    # Connection and Login Functions
    def connect_prompt(self):
        self.display_text_output('Kembra Station')
        self.display_text_output('By Biff Willoughbers')
        self.display_text_output('To join a game, enter a server address to connect to: ')

        self.bind_connect()

    def login_prompt(self):
        self.bind_login()
        self.display_text_output('Your essence is drawn through space and time to a particular point.', color_code='narrator')
        self.display_text_output('You sense your destination is nearing...', color_code='narrator')
        self.display_text_output('As you are pulled into the fire, you must decide: Who are you?', color_code='narrator')

        self.bind_login()

    def connect(self, event):
        server_ip = self.get_player_input()

        if not self.validate_server_ip(server_ip):
            return False

        try:
            print('trying to connect to: ', self.server_ip)
            self.socket.connect((self.server_ip, PORT))
        except socket.timeout as e:
            self.display_text_output(
                f'Attempt to connect to {self.server_ip} timed out. Please check server status and try again.')
            self.refresh_socket()
            print(e)
        except socket.gaierror:
            self.display_text_output(f'{self.server_ip} is not a valid server address.')
        else:
            print(f'Connected to host at {server_ip}.')
            self.login_prompt()

    def validate_server_ip(self, server_ip):
        valid_chars = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.']
        for char in server_ip:
            if char not in valid_chars:
                self.display_text_output(f'{server_ip} is not a valid server address. Provide a valid address to connect to.', command_readback=True)
                return False

        self.server_ip = server_ip
        return True

    def login(self, event):
        login_name = self.get_player_input()

        if not login_name:
            self.display_text_output('You must give a name to incarnate.', color_code='narrator')
            return False

        if not login_name.isalpha():
            self.display_text_output('One\'s name must be speakable. Offer another...', color_code='narrator')
            return False

        self.send_message(login_name)

        response_header = self.socket.recv(HEADER_LENGTH).decode('utf-8')
        if not len(response_header):
            return False
        response_length = int(response_header)
        login_response = self.socket.recv(response_length).decode('utf-8')

        self.display_text_output(login_response)
        self.bind_game_keys()
        
        self.listen_thread = threading.Thread(target=self.listen_for_broadcasts, name='listen thread')
        self.listen_thread.start()

    def refresh_socket(self):
        self.socket.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(TIMEOUT)

    def listen_for_broadcasts(self):
        self.socket.setblocking(True)

        while True:
            try:
                broadcast_header = self.socket.recv(HEADER_LENGTH)
                if not broadcast_header:
                    return
                broadcast_length = int(broadcast_header.decode('utf-8'))
                broadcast = self.socket.recv(broadcast_length).decode('utf-8')
                self.display_text_output(broadcast)
            except RuntimeError as e:
                print(f'RuntimeError: {e}. Goodbye!')
                return

    # User Input Handling

    def process_input(self, event):
        player_input = self.get_player_input()
        self.display_text_output(player_input, command_readback=True)

        if player_input == 'quit':
            self.quit()
            return None
        elif player_input == 'menu':
            pass

        words = player_input.lower().split()

        if len(words) == 0: # Is this necessary / proper handling?
            self.display_text_output('Please enter something.')
            return None

        if words[0] in actions.verb_list or words[0][0] in ['"', '\'']: # this could be a function called here. Actually I'm not sure the "clean code" way to do it
            player_command = self.parse_player_input(words)
            self.send_command(player_command)

        else:
            self.display_text_output(f'You want to {words[0]}? I don\'t even know what that is...', color_code='narrator')
            return False

    def parse_player_input(self, words):
        player_command = actions.Command()

        # There are some special handling cases that do not use [verb: the rest] format
        # Including move directions, and speaking with
        # A supplementary function can be designed later, but for now they will be parsed and handled here
        if len(words) == 1 and words[0] in ['n', 'north', 'e', 'east', 'w', 'west', 's', 'south']:
            player_command.verb = 'go'
            player_command.target = self.clean_direction(words[0])
            return player_command # If safe, remove this and rely on function's primary return line

        if words[0][0] in ['\'', '"', '!']:
            if words[0][0] == '!':
                player_command.verb = 'yell'
            else:
                player_command.verb = 'speak'
            words[0] = words[0][1:]
            player_command.target = ' '.join(words)
            return player_command

        # This marks the start of the function's standard intent
        # grab verb, chop it off list
        player_command.verb = words[0]
        del words[0]

        if len(words) == 1:
            player_command.target = words[0]

        return player_command

    def clean_direction(self, direction):
        if direction == 'n':
            return 'north'
        elif direction == 's':
            return 'south'
        elif direction == 'e':
            return 'east'
        elif direction == 'w':
            return 'west'
        else:
            return direction

    def send_command(self, action_command, code='01'):
        pickled_action_command = pickle.dumps(action_command)
        self.socket.send(code.encode('utf-8'))
        self.socket.send(pickled_action_command)

    def send_message(self, message, code='00'):

        if code == '00':
            message_header = f'{len(message):<{HEADER_LENGTH}}'

            print(f'Sending: {message}')
            self.socket.send(code.encode('utf-8'))
            self.socket.send(message_header.encode('utf-8') + message.encode('utf-8'))

    # ---- Key Bindings

    def bind_connect(self):
        self.unbind_game_keys()

        BOUND_KEYS.append('<Return>')
        self.bind('<Return>', self.connect)

    def bind_login(self):
        self.unbind_game_keys()

        BOUND_KEYS.append('<Return>')
        self.bind('<Return>', self.login)

    def bind_game_keys(self):
        self.unbind_game_keys()

        BOUND_KEYS.append('<Return>')
        self.bind('<Return>', self.process_input)
        print('Game Keys Active')

    def bind_client_level_keys(self):
        self.bind('<Escape>', self.escape_main_menu)

    def unbind_game_keys(self):
        for bound_key in BOUND_KEYS:
            self.unbind(bound_key)

    def escape_main_menu(self, event):
        self.main_menu()

    # ---- Menu

    def main_menu(self):
        # Opens small popup menu, a la aoe2
        pass

    # ---- System

    def start(self):
        self.main_menu()
        self.mainloop()

    def quit(self):
        if self.socket:
            self.socket.shutdown(socket.SHUT_WR)
        self.destroy()
        quit()

    # ---- Text Display

    def get_player_input(self):

        player_input_text = self.game_screen.player_input.get(1.0, 'end-2l lineend')
        self.game_screen.player_input.delete(1.0, 'end')

        return player_input_text

    def enter_to_continue(self):
        # Make a function which takes function as argument. '<Return>' gets bound with a function that prints the next
        # line when user hits key. This way user can "scroll" through story dialog, not have it all pop up at once.
        pass

    def display_text_output(self, text, pattern1=None, tag1=None, pattern2=None, tag2=None, command_readback=False,
                            color_code='default'):

        # It should not be hard to detect wrappers around specific spans of the packet string to be colored.

        if '||' in text:
            ftexts = text.split('||')
            del ftexts[0]
            print(ftexts)
            for ft in ftexts:
                fcode = ft[:5]  # Relates to the constant dict FCODES, to assign color code
                ftext = ft[5:]
                if fcode == "TITLE":
                    ftext = f'{ftext:<{100}}'
                self.game_screen.output_display.display_text(f'{ftext}\n')
                self.game_screen.output_display.apply_tag_to_pattern(ftext, FCODES[fcode])

        else:
            self.game_screen.output_display.display_text(text)
            if color_code == 'speech':
                self.game_screen.output_display.apply_tag_to_pattern(text, 'light-turquoise')
            elif color_code == 'narrator':
                self.game_screen.output_display.apply_tag_to_pattern(text, 'light-lavender')

            if command_readback:
                self.game_screen.output_display.display_text('\n')
            else:
                self.game_screen.output_display.display_text('\n>')


if __name__ == "__main__":
    client = Client()
    client.start()

'''
Documentation:

'''