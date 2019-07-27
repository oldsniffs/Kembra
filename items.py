import os
import xml.etree.ElementTree as et

base_path = os.path.dirname(os.path.realpath(__file__))
items_xml = os.path.join(base_path, 'data\\items.xml')
items_parse = et.parse(items_xml)
items_root = items_parse.getroot()

# Might only use one of these in the end
all_terminal_items = []
all_item_names = []
all_terminal_item_names = []

class Item:

	def describe(self):
		best_description = self.description
		return best_description

	# This method is commented out because items probably won't need to use Game()'s display_text_output. If they do, a way to get a reference in will be needed.
	# def __getstate__(self):
	# 	state = self.__dict__.copy()
	# 	del state['game']
	# 	return state

class Consumable(Item):
	def __init__(self):
		super().__init__()

class Food(Consumable):
	def __init__(self):
		super().__init__()

class Fish(Food): 
	def __init__(self):
		super().__init__()

	# if cooked, that should be reflected in name, display name, or description

class Stanget(Fish):
	def __init__(self):
		super().__init__()

class Cremip(Fish):
	def __init__(self):
		super().__init__()

class Weapon(Item):
	def __init__(self):
		super().__init__()

class Arrow(Weapon):
	def __init__(self):
		super().__init__()
		self.quantity=1


# Checks each subclass for readin attribute. If present, starts reading in data.
# An alternative would be to get a list of all terminal subclasses, and match to xml trees by name.
def readin_item_data(the_class, node):
	# Does something extra: Adds name of each terminal class to list of all_item_names.
	for sc in the_class.__subclasses__():
		for child in node:
			if class_to_tag(sc) == child.tag:
				if 'readin' in child.attrib:
					for attr_elem in child:
						if attr_elem.tag not in [class_to_tag(ssc) for ssc in sc.__subclasses__()]: # This means the tag does not relate to another subclass, and should be read in as an attribute.
							value = attr_elem.text
							# print(attr_elem.tag, value)
							if not attr_elem.text:
								continue
							if attr_elem.text.isdigit() == False:
								value = '\''+value+'\''
							exec(sc.__name__+'.'+attr_elem.tag+' ='+value)
							# This line used to be in place above, but I don't remember why I had been using property. Doesn't seem needed
							# exec(sc.__name__+'.'+attr_elem.tag+' = property(lambda self: '+value+')')
							# There is a drawback: These dynamically added vars aren't mapped to the item __dict__.  A custom mapping function could add them to a list if needed.
				readin_item_data(sc, child)
		if 'name' in dir(sc): # PROBLEM : plural terms getting double added
			all_item_names.append(sc.name)
			if sc.plural_name not in all_item_names:
				#print(sc.plural_name+' not in ', all_item_names, ' -adding now.')
				all_item_names.append(sc.plural_name)
			all_item_names.append(sc.plural_name)
			if sc.__subclasses__() == []:
				all_terminal_item_names.append(sc.name)
				all_terminal_items.append(sc)
				if sc.plural_name not in all_terminal_item_names:
					#print(sc.plural_name + ' not in ', all_terminal_item_names, ' -adding now')
					all_terminal_item_names.append(sc.plural_name)



def class_to_tag(a_class):

	class_name = a_class.__name__.lower()
	no_change_for_plural = ['fish'] 

	# Makes sure tags for classes without subs remain in singular form
	if a_class.__subclasses__() == [] or class_name in no_change_for_plural:
		return class_name

	else:
		result = class_name + 's'

	return result

def class_var_from_element():
	pass

readin_item_data(Item, items_root)

# Multiple inheritance like cookables and consumables?

# ---- if __name__ == '__main__' ----

if __name__ == '__main__':

	print(all_item_names)
	print(all_terminal_item_names)


	# print(items_root)
	# for child in items_root:
	# 	print(child.tag, child.attrib)
	# print(class_to_tag(Item))
	# print(Item.__name__)
	# print(Item.__subclasses__())
	# print(Fish.__subclasses__())
	# fish = Fish()
	# print(fish.__dict__)
