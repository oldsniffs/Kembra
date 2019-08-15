# Home of action_command shit, including verb lists, and parse and execute functions

"""
TODO: Checks for whether a target has been given by user should be done in client, and not sent without one.
TODO: Implement reassign_if_move_direction to proper place
TODO: A covert system. Subject attempts to do something hidden, a check is performed for others to view it

"""


system_commands = ['main menu', 'pause', 'quit']
player_only_verbs = ['i', 'inv', 'inventory', 'friends']
world_verbs = ['speak', 'look', 'go', 'n', 'north', 'e', 'east', 'w', 'west', 's', 'south']
subject_verbs = ['eat', 'drink']  # Subject acts on self
interaction_verbs = ['talk', 'shop', 'buy', 'sell', 'give']  # Involves other people
item_verbs = ['get', 'take', 'drop']
verb_list = world_verbs + subject_verbs + interaction_verbs + item_verbs + player_only_verbs

ALL_VALID_TARGETS = ''


class Action:
    def __init__(self, subject=None, verb=None): # delete verb argument, it's here just for now to dev functions
        self.subject = subject
        self.verb = verb
        self.target = None
        self.direct_object = None
        self.quantity = 0
        print(self.verb)

        self.end_time = 0

        # These 2 require server side validation to properly instantiate. A more elegant solution in the future
        # Also, really seems this is not the best way to get a reference to the server in the class
        self.action_function = None
        self.server = None

    def execute(self):
        self.action_function = eval(self.verb)

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


def get_opposite_direction(target):
    opposite_dir = ''

    if target == 'north':
        opposite_dir = 'south'
    elif target == 'east':
        opposite_dir = 'west'
    elif target == 'west':
        opposite_dir = 'east'
    elif target == 'south':
        opposite_dir = 'north'

    return opposite_dir


def go(action_command):
    if not action_command.target:
        response = 'Where do you want to go?'

    elif action_command.target in ['n', 'e', 'w', 's', 'north', 'east', 'west', 'south']:
        arrive_from_direction = get_opposite_direction(action_command.target)

        if action_command.target in action_command.subject.location.get_exits():
            player_observers, ai_observers = get_observers(action_command)
            current_observation = f'{action_command.subject.name} leaves heading {action_command.target}.'
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


def speak(action_command):

    for person in action_command.subject.location.denizens:
        if type(person).__name__ == 'Player' and person!= action_command.subject:
            print(person.name)
            action_command.server.queue_broadcast(person, f'{action_command.subject.name} says, "{action_command.target}"')

    response = f'You say, "{action_command.target}"'
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

def validate_target(action_command):
    pass
    # General all-size validation
