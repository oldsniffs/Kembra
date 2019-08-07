import items
import random

# TODO: Cartography skill lets you make maps from your explorations.

mb_male_weights = {
	'istj': 164,
	'estj': 112,
	'istp': 85,
	'isfj': 81,
	'isfp': 76,
	'esfj': 75,
	'esfp': 69,
	'enfp': 64,
	'estp': 56,
	'intp': 48,
	'infp': 41,
	'entp': 40,
	'intj': 33,
	'entj': 27,
	'enfj': 16,
	'infj': 12
}
mb_female_weights = {
	'isfj': 194,
	'esfj': 169,
	'esfp': 101,
	'isfp': 99,
	'enfp': 97,
	'istj': 69,
	'estj': 63,
	'infp': 46,
	'enfj': 33,
	'estp': 30,
	'entp': 24,
	'istp': 23,
	'intp': 17,
	'infj': 16,
	'intj': 9,
	'entj': 9
}

def random_mb():
	mb = 1
	return mb

# What they spend their time doing. Might only want 1 per CarbonLife
class Vocation():
	def __init__(self):
		self.name = ''


class CarbonLife(): # Could inherit CarbonLife
	def __init__(self, world, name): # vocation, skills, attributes): #

		self.world = world
		self.name = name
		self.description = self.name

		# Behavior
		self.active = False
		self.behavior_state = None

		self.relationships = {} # target: number/string rank

		self.location = self.world.map[(10,10)].map[(1,5,7)]

		self.inventory = []

		# Biometrics
		self.gender = ''
		self.height = 0
		self.weight = 0 # weight formula tbd

		self.add_to_world()

	def add_to_world(self):
		self.world.all_people_names.append(self.name)
		self.location.denizens.append(self)
		self.world.ai_population.append(self)

	def describe(self):
		pass
		# Height, weight, etc adjectives based on biometric values. Clothes as well?

# ---- Actions ----

	def detect_action(self, action):
		if self.location == action.subject.location:
			detected = True
		else:
			detected = False
		return detected

	def get_item(self, item, target=None): # Needs source argument for containers, people, not just taking from location items
		# Needs to handle quantities: get stangets, get 2 stangets
		if target==None:
			self.inventory.append(item)
			self.location.items.remove(item)

		else:
			self.inventory.append(item)
			target.items.remove(item)

	def move(self, direction=None, exit=None):
		# Still open question of directional movement into new zone

		if exit:
			self.location = exit.destination

		elif direction:
			new_xyz = list(self.location.xyz)
			if direction == 'north':
				new_xyz[1] += 1
			if direction == 'east':
				new_xyz[0] += 1
			if direction == 'west':
				new_xyz[0] -= 1
			if direction == 'south':
				new_xyz[1] -= 1

			self.location.denizens.remove(self)
			self.location = self.location.zone.map[tuple(new_xyz)]
			self.location.denizens.append(self)

	def say(self, speech):
		self.world.world_events

	# ---- Support methods ----

	def copy_xyz_list(self, xyz):
		return list(tuple(xyz))

	def get_inventory(self): # Check through bags

		items_description = ''

		if len(self.inventory)==1:
			items_description = 'There is a ' + self.inventory[0].name + ' here.'
		elif len(self.inventory) > 1: 
			items_description = 'There are '

			# Sorts items into stacks, grouped, and single
			single_items = []
			grouped_items = {}
			checked_list = []
			for i in self.inventory:
				if i.name in checked_list:
					continue
				if i.grouping == 'normal':
					count = 1
					for i_duplicate in self.inventory:
						if i_duplicate != i and i.name == i_duplicate.name:
							count += 1
							checked_list.append(i.name)

					if count == 1:
						single_items.append(i)
					if count > 1:
						grouped_items[i.plural_name] = count

				elif i.grouping == 'stack':
					single_items.append(i)

				else:
					single_items.append(i)

			grouped_count = len(grouped_items)
			single_count = len(single_items)

			for i, q in grouped_items.items():
				if grouped_count == 1 and single_count == 1: # If there were only 2 item listings, no comma needed
					items_description = items_description + str(q) + ' ' + i + ' '
				elif grouped_count > 1 or single_count != 0:
					items_description = items_description + str(q) + ' ' + i+', '
				elif grouped_count == 1:
					items_description = items_description+str(count)+' '+i+' here'
				else:
					items_description = items_description + 'and '+str(count)+' '+i+' here.'
				grouped_count -= 1
				
			for i in single_items:
				if single_count == 2 and len(self.inventory) == 2: # If there were only 2 item listings, no comma needed
					if i.grouping == 'stack':
						items_description = items_description + 'a ' +i.stack_name+' of '+i.plural_name+' '
					else:
						items_description = items_description + 'a ' + i.name + ' '
				if single_count > 1:
					if i.grouping == 'stack':
						items_description = items_description + 'a '+i.stack_name+' of '+i.plural_name+', '
					else:
						items_description = items_description + 'a ' + i.name + ', '
				else:
					if i.grouping == 'stack':
						items_description = items_description+'and a '+i.stack_name+' of '+str(i.quantity)+' '+i.plural_name+' here.'
					else:
						items_description = items_description + 'and a ' + i.name+' here.'
				single_count -= 1

		return items_description

	def __getstate__(self):
		state = self.__dict__.copy()
		del state['game']
		return state


class Player(CarbonLife):
	def __init__(self, world, name):
		super().__init__(world, name)
		self.inventory = [items.Stanget()]

	def add_to_world(self):
		self.world.players.append(self)
		self.world.all_people_names.append(self.name)
		self.location.denizens.append(self)

	def show_location(self):
		current_location = 'You are at ' + self.location.zone.name + ', ' + self.location.name + '.'
		return current_location

	def generate_player(self):
		pass

	def look(self):
		return self.location.describe(observer=self)


class AI(CarbonLife):
	def __init__(self, world, name):
		super().__init__(world, name)

		# Personal Background
		self.mb = None
		self.vocation = None

		self.current_action = None
		self.action_timer = self.get_action_timer()

	def determine_behavior(self):
		needs = self.check_needs

	def check_needs(self):
		# Check hunger, thirst, sleep, urgent necessities
		pass

	def meet_n_greet(self):
		for d in self.location.denizens:
			if d not in self.relationships.keys():
				pass



class Animal(CarbonLife):
	pass

# ---- if __name__ == '__main__' ----

if __name__ == '__main__':
	pass