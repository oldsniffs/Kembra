# This file contains all map related objects

import people
import os
import xml.etree.ElementTree as et
import queue

# TODO: Can the following code be moved into World.load_map ?
# TODO: Different exit generation for outdoors (open) vs indoors?

base_path = os.path.dirname(os.path.realpath(__file__))
locations_xml = os.path.join(base_path, 'data\\locations.xml')
locations_tree = et.parse(locations_xml)

world_tree = locations_tree.getroot()

class World:
	def __init__(self):
		self.map = {}
		self.load_map()

		self.high_priority_timers = queue.Queue()
		self.low_priority_timers = queue.Queue()

		self.players = []
		self.players.append(people.Player(self, 'Fred'))

		self.populate()

	def load_map(self):
		for zone in world_tree:
			new_zone_xy = eval('(' + zone[0].text + ')')
			new_zone_type = zone[1].text
			new_zone_name = zone[2].text
			new_zone_description = zone[3].text

			self.map[new_zone_xy] = Zone(new_zone_xy, new_zone_type, new_zone_name, new_zone_description)

			# Instantiate location objects from locations.xml
			for location in zone[4]:
				new_location_xyz = eval('(' + location[0].text + ')')
				new_location_zone = self.map[new_zone_xy]
				new_location_name = location[1].text
				new_location_physical_description = location[2].text

				new_location_items = []
				# This could be done as a loop
				if not location[3].text:
					new_location_harvestables = []
				else:
					new_location_harvestables = location[3].text.split(',')
				if location[4].text == None:
					new_location_interactables = []
				else:
					new_location_interactables = location[4].text.split()
				if location[5].text == None:
					new_location_items = []
				else:
					for i in location[5]:
						new_item_dict = {}
						
						for e in i:
							new_item_dict[e.tag] = e.text
								# Still need a line to e.text convert to appropriate digit
						new_location_items.append(self.place_item(new_item_dict))

				self.map[new_zone_xy].map[new_location_xyz] = Location(new_location_xyz, new_location_zone, new_location_name, new_location_physical_description, new_location_harvestables, new_location_interactables, new_location_items)

	def place_item(self, item_dict):
		new_item_dict = item_dict # This copy might not be needed

		new_item = eval('people.items.' + item_dict['item_class'] + '()')
		del new_item_dict['item_class']

		for key, value in new_item_dict.items():

			exec('new_item.'+key+' = '+value)

		
		return new_item

	def populate(self):
		pass

class Zone:
	def __init__(self, xyz, type, name, description):
		self.xyz = xyz
		self.type = type
		self.name = name
		self.description = description
		self.map = {} # Key is (x,y) tuple, value is Location object


class Location:
	def __init__(self, xyz, zone, name, physical_description, harvestables, interactables, items):
		self.xyz = xyz
		self.zone = zone
		self.name = name
		self.denizens = []
		self.physical_description = physical_description
		self.harvestables = harvestables
		self.interactables = interactables
		self.items = items
		self.buildings = []
		self.special_exits = [] # For special exits where directional movement does not apply

	def get_viewables(self):
		return self.items + self.denizens + self.harvestables + self.interactables + self.special_exits

	def get_exits(self):

		exits = []

		west_xyz = (self.xyz[0]-1, self.xyz[1], self.xyz[2])
		east_xyz = (self.xyz[0]+1, self.xyz[1], self.xyz[2])
		south_xyz = (self.xyz[0], self.xyz[1]-1, self.xyz[2])
		north_xyz = (self.xyz[0], self.xyz[1]+1, self.xyz[2])

		if west_xyz in self.zone.map.keys():
			exits.append('west')
		if east_xyz in self.zone.map.keys():
			exits.append('east')
		if south_xyz in self.zone.map.keys():
			exits.append('south')
		if north_xyz in self.zone.map.keys():
			exits.append('north')

		for se in self.special_exits:
			if se.detected:
				exits.append(se.name)

		return exits

	def capitalize_exits(self):
		capitalized_exits = []
		for e in self.get_exits():
			capitalized_exits.append(e.capitalize())
		return ', '.join(capitalized_exits)

	def describe(self, observer=None):
		# TODO: Maybe rename this as look as it provides live updated info.

		description = f'||TITLE{self.zone.type}, {self.zone.name}: {self.name}||PHYSD{self.physical_description}'

		# This algorithm (when complete) can be reused to list items in any inventory style list
		if len(self.items) > 0:
			items_description = ''
			if len(self.items) == 1:
				items_description = '\nThere is a ' + self.items[0].name + ' here.'
			elif len(self.items) > 1:
				items_description = '\nThere are '

				# Sorts items into stacks, grouped, and single
				single_items = []
				grouped_items = {}
				checked_list = []
				for i in self.items:
					if i.name in checked_list:
						continue
					if i.grouping == 'normal':
						count = 1
						for i_duplicate in self.items:
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
					else:
						items_description = items_description + 'and '+count+' '+i+' here.'
					grouped_count -= 1

				for i in single_items:
					if single_count == 2 and len(self.items) == 2: # If there were only 2 item listings, no comma needed
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

			description = description + f'||ITEMS{items_description}'

		denizens_description = ''
		for denizen in self.denizens:
			if denizen == observer:
				continue
			denizens_description = denizens_description + f' {denizen.name}'

		if denizens_description:
			description = description + f'||DENZSOthers present:{denizens_description}'

		description = description + f'||EXITSAvailable Exits: {self.capitalize_exits()}'

		return description


class SpecialExit:
	def __init__(self):
		pass


class Building:
	def __init__(self):
		self.name = ''
		self.size = 0
		self.rooms = {}


class Room: # Possible inheritance from Location
	def __init__(self):
		self.name = ''
		self.size = 0


# ---- Testing functions ----


if __name__ == '__main__':
	world=World()
	for l in world.map[(10,10)].map:
		print(l)
	print(world.map[(10,10)].map[(1,5,7)].describe())
	print(world.map[(10,10)].map[(1,4,7)].denizens)
