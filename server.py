import tkinter as tk
import shelve
import os
import threading

import network
import locations
import ui


class ServerApp(tk.Tk):
    def __init__(self):
        self.world = None

        self.title('Hearthfire Server')
        self.geometry('1500x800')
        self.config(background='black')

        self.frames = {}

        self.current_game = 'No game active'
        self.create_widgets()

    def create_widgets(self):
        self.game_screen = ui.GameScreen()
        self.game_screen.pack

    def get_player_input(self):
        return self.game_screen.player_input.get()

    def process_command(self):
        command = self.get_player_input()

        if command == 'start':
            pass

    def show_frame(self):
        pass


class Menu(tk.Frame):
    def __init__(self, parent):

        self.base_path = os.path.dirname(os.path.realpath(__file__))
        self.save_path = os.path.join(self.base_path, 'saves')
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def new_world(self):
        # Stop the world event watcher loop
        self.world = locations.World()
        network.run_world(self.world)
        network.run_server(self.world)

    def save_world(self):
        # Stop world timer
        save_name = self.save_name_entry.get()

        d = shelve.open(self.save_path + '/' + save_name)
        d['world'] = self.world

    def create_widgets(self):

        self.save_frame = tk.Frame()
        self.default_frame = tk.Frame()

        self.save_entry_var = tk.StringVar()
        self.save_entry_var.trace('w', self.toggle_save_button)
        self.save_entry = tk.Entry(self.save_frame, textvariable=self.save_entry_var)
        self.save_button = tk.Button(self.save_frame, text='Save World', command=self.save_world)

        self.save_button.pack()
        self.save_entry.pack()

    def toggle_save_button(self, *args):
        x = self.save_entry_var.get()
        if len(x) > 0:
            self.save_button.config(state='normal')
        if len(x) == 0:
            self.save_button.config(stat='disabled')


server_thread = threading.Thread(target=network.run_server, name='server thread', args=(locations.World(),))
server_thread.start()
