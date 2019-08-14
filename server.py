import threading
import time

import network
import locations


def run_world(world): # Move to World class? Cant' see why not
    # another loop to update player actions
    # and one for harvestables, interactables. Could these lower priority updates occur less frequently?
    # Use time%{number of seconds} to set priority / frequency of different loop checks
    for ai in world.ai_population:
        if ai.current_action:
            if ai.current_action.end_time < time.time():
                continue
            else:
                ai.current_action.execute()
                ai.determine_action()

        else:
            continue

    for player in world.active_players:
        if player.current_action.end_time < time.time():
            pass


class ServerApp: # In the future, this class will extend tk.Tk as a GUI
    def __init__(self):
        self.server = network.Server()
        self.world = locations.World()
        self.world.server = self.server

        self.server_thread = threading.Thread(target=self.server.run_server, name='server thread', args=(self.world,))
        self.world_thread = threading.Thread(target=run_world, name='run world thread', args=(self.world,))


server_app = ServerApp()
server_app.world_thread.start()
server_app.server_thread.start()
