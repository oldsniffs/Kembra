import threading
import time


import network
import locations


# The Central Loop
def run_world(world): # Move to World class? Cant' see why not
    # another loop to update player actions
    # and one for harvestables, interactables. Could these lower priority updates occur less frequently?
    # Use time%{number of seconds} to set priority / frequency of different loop checks
    while True:
        for ai in world.ai_population:  # If there are syncing issues, queues might solve it
            if ai.current_action:
                if ai.current_action.completion_time <= world.get_time(): # can we just get smaller value, as in just check
                    # seconds without fucking things up when the minute changes? There should be a way, if that is more efficient.
                    continue
                else:
                    ai.current_action.execute()
                    ai.determine_action()

            else:
                ai.determine_action()

        for player in world.active_players:
            if player.current_action:
                if player.current_action.completion_time <= world.clock.now():
                    print(f'Action completion time: {player.current_action.completion_time} <= {world.clock.now()}-- executing {player.current_action.action_function}')
                    player.current_action.execute()


class ServerApp: # In the future, this class will extend tk.Tk as a GUI
    def __init__(self):
        self.server = network.Server()
        self.world = locations.World()
        self.world.server = self.server


server_app = ServerApp()

server_thread = threading.Thread(target=server_app.server.run_server, name='server thread', args=(server_app.world,))
server_thread.start()

run_world(server_app.world)
