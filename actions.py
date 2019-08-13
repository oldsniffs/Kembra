# Home of action_command shit, including verb lists, and parse and execute functions

"""
TODO: Checks for whether a target has been given by user should be done in client, and not sent without one.
TODO: Implement reassign_if_move_direction to proper place
TODO: A covert system. Subject attempts to do something hidden, a check is performed for others to view it

"""

# For Reference
"""
From network, code to broadcast observations
if response:
    self.broadcast(sock, response)
if observed_message:
    for s in [s for s in self.sockets if s != sock and s != self.server]:
        if self.active_players[s].detect_action(player_action):
            self.broadcast(s, observed_message)
"""


system_commands = ['main menu', 'pause', 'quit']
player_only_verbs = ['i', 'inv', 'inventory', 'friends']
world_verbs = ['look', 'go', 'n', 'north', 'e', 'east', 'w', 'west', 's', 'south']
subject_verbs = ['eat', 'drink']  # Subject acts on self
social_verbs = ['talk', 'shop', 'buy', 'sell', 'give']  # Involves other people
item_verbs = ['get', 'take', 'drop']
verb_list = world_verbs + subject_verbs + social_verbs + item_verbs + player_only_verbs

ALL_VALID_TARGETS = ''


class ActionCommand:
    def __init__(self, verb, subject): # delete verb argument, it's here just for now to dev functions
        self.subject = subject
        self.verb = verb
        self.target = None
        self.direct_object = None
        self.quantity = 0
        print(self.verb)

        self.end_time = 0
        self.action_function = eval(self.verb)
        self.server = self.subject.server

    def execute(self):

        print(self.server.broadcast_queues, self.subject.name, self.subject.socket)
        response = self.action_function(self)
        if self.subject in self.server.active_players.values():
            if response:
                self.server.queue_broadcast(self.subject, response)


def look(action_command):
    # TODO: Location items could have a description of where in the room they are.
    #  If in inventory, this response could include that - "The cremip in your bag ... "

    if not action_command.target:
        response = action_command.subject.look()

    else:
        present_viewables = action_command.subject.location.get_viewables() + action_command.subject.inventory
        for pv in present_viewables:
            # Eventually, this try/except shouldn't be needed as all items can be safely assumed to have a name
            # and description
            try:
                if pv.name.lower() == action_command.target:
                    response = pv.description
                    break  # Break makes it stops after finding first match.
            except AttributeError as e:
                print(f'{pv} raised error: {e}')
        if response is None:
            response = f'{action_command.target} not found here.'

    return response


def get_go_directions(target):
    clean_target = ''
    opposite_dir = ''

    # n to north to be done in client side parsing
    if target == 'n' or target == 'north':
        clean_target = 'north'
        opposite_dir = 'south'
    elif target == 'e' or target == 'east':
        clean_target = 'east'
        opposite_dir = 'west'
    elif target == 'w' or target == 'west':
        clean_target = 'west'
        opposite_dir = 'east'
    elif target == 's' or target == 'south':
        clean_target = 'south'
        opposite_dir = 'north'

    return clean_target, opposite_dir


def go(action_command):
    if not action_command.target:
        response = 'Where do you want to go?'

    elif action_command.target in ['n', 'e', 'w', 's', 'north', 'east', 'west', 'south']:
        departing_direction, arrive_from_direction = get_go_directions(action_command.target)

        if action_command.target in action_command.subject.location.get_exits():
            player_observers, ai_observers = get_observers(action_command)
            current_observation = f'{action_command.subject.name} leaves heading {departing_direction}.'
            for player_observer in player_observers:
                action_command.server.queue_broadcast(player_observer, current_observation)

            action_command.subject.move(direction=action_command.target)

            player_observers, ai_observers = get_observers(action_command)
            current_observation = f'{action_command.subject.name} arrives from the {arrive_from_direction}.'
            for player_observer in player_observers:
                action_command.server.queue_broadcast(player_observer, current_observation)

            response = action_command.subject.look()

        else:
            response = 'You can\'t go that way!'

    elif action_command.target: # Tighten this conditional with list comprehension
        for es in action_command.subject.location.special_exits:
            if action_command.target == es.name:
                action_command.subject.move(exit=es)

    else:
        response = 'I don\'t understand where you\'re trying to go.'

    return response


def get_observers(action_command):
    # Players
    player_observers = []
    ai_observers = []
    for active_player in action_command.server.active_players.values():
        if active_player.detect_action(action_command) and active_player != action_command.subject:
            player_observers.append(active_player)

    return player_observers, ai_observers


def execute_action_command(action_command):

    if action_command.verb == 'get':

        if not action_command.target:
            response = 'What do you want to get?'

        else:
            for i in action_command.subject.location.items:
                if i.name == action_command.target:
                    action_command.subject.location.items.remove(i)
                    action_command.subject.inventory.append(i)
                    # TODO: As of now it picks up 1st match and stops.
                    #  Could pick up all, prompt user to pick up all, or user can enter pick up all items
                    break

        response = f'You get the {action_command.target}'
        observation = f'{action_command.subject.name} picks up {action_command.target}'

    return response, observation


def parse_player_action(player, verb, words): # Gonna get cut

    player_action = ActionCommand(verb, player)
    print(f'player at parse: {player}')

    # strip() in case value is blank space. may not be necessary
    words = words.split()

    # I would check action instead of words, but unsure about blank space.
    if not words:
        return player_action

    if len(words) == 1:
        print(f'assigning {words[0]} as target')
        player_action.target = words[0]

    return player_action
