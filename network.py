import select
import socket
import queue
import time

import people
import actions

"""
TODO: Lost socket function to close out connection, remove temp assets

TODO: Login function
"""

""" Development Notes

server.py creates world object and runs server with functions here
Tracks changes to player objects and their locations associated with connected clients and notifies affected clients as
necessary.
Listens for commands from clients, returns a message regarding the command if needed.

Question of using a Client class: Operations will be more granular with a class. But are needs that complex? 
"""

HEADER_LENGTH = 10
VERB_HEADER_LENGTH = 10
CODE_LENGTH = 2
HEADER_AND_CODE = HEADER_LENGTH + 2

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = '10.0.0.43'
port = 1234
server.bind((server_address, port))
server.listen(5)

sockets = [server]
actionable_sockets = []
active_players = {}  # {client: player}
message_queues = {}
command_queues = {}
online_player_locations = []

world_events = []


def receive_message(client_socket):

	try:
		print(client_socket)
		header = client_socket.recv(HEADER_LENGTH).decode('utf-8')
		code = client_socket.recv(CODE_LENGTH).decode('utf-8')

		if not len(header):
			raise Exception

		message_length = int(header)
		message = client_socket.recv(message_length).decode('utf-8')

		return code, message

	except ConnectionResetError as e:
		print(f'ConnectionResetError from {client_socket.getsockname()}: {e}')
		return None, None


def broadcast(client_socket, message):
	broadcast_header = f'{len(message):<{HEADER_LENGTH}}'
	print(f'Broadcasting to {client_socket.getsockname()}: {broadcast_header} {message}')
	client_socket.send(broadcast_header.encode('utf-8') + message.encode('utf-8'))


def run_server(world):
	print('Server online: Accepting connections...')
	while True:
		readables, actionables, exceptionals = select.select(sockets, actionable_sockets, sockets)

		for sock in readables:
			if sock == server:

				new_client, client_address = server.accept()
				new_client.setblocking(False)
				print(f'Connection from {client_address[0]}:{client_address[1]} established')
				sockets.append(new_client)
				message_queues[new_client] = queue.Queue()
				command_queues[new_client] = queue.Queue()

			elif sock in sockets:
				try:
					code, data = receive_message(sock)
				except Exception as e:
					print('Exception reached: ', e)
					close_client(sock)
					continue

				if sock not in active_players:
					login_name = data
					if not login_name:
						print(f'(From Readables) Lost connection from {sock.getsockname()}.')
						# TODO: When up and running, try using close method here
						# TODO: Is following code needed?
						if sock in actionable_sockets:
							actionable_sockets.remove(sock)
						if sock in active_players:
							del active_players[sock]
						sockets.remove(sock)
						del message_queues[sock]
						del command_queues[sock]
						sock.close()

					if login_name in [player.name for player in world.players]:
						for player in world.players:
							if login_name == player.name:
								active_players[sock] = player
								print(f'{sock.getsockname} logged in as {active_players[sock].name}')
								broadcast(sock, f'Logged in as {active_players[sock].name}.')
					else:
						active_players[sock] = people.Player(world, login_name)
						print(f'New player {login_name} created by {sock.getsockname()}')
						world.players.append(active_players[sock])
						broadcast(sock, f'Welcome to the world, {active_players[sock].name}')

				else:
					if code == '01':
						verb = data[:10].strip()
						action = data[10:]
						print(f'Received (verb: action) {verb}: {action}')

						player_action = actions.parse_player_action(active_players[sock], verb, action)
						response, observed_message = actions.execute_player_action(player_action)
						if response:
							broadcast(sock, response)
						if observed_message:
							for s in [s for s in sockets if s != sock and s != server]:
								if active_players[s].detect_action(player_action):
									broadcast(s, observed_message)

					elif code == '00':
						pass

					elif code == '02':
						if data[0] == '\'':
							for s in [s for s in sockets if s != server]:
								if active_players[s].location == active_players[sock].location:
									broadcast(s, f'{active_players[sock].name} says, "{data[1:]}"')
						if data[0] == '!':
							for s in [s for s in sockets if s != server]:
								if active_players[s].location == active_players[sock].location:
									broadcast(s, f'{active_players[sock].name} yells, "{data[1:]}!"')

		for sock in exceptionals:
			print(f'(From exceptionals list) Lost connection from {sock.getsockname()}.')
			if sock in actionable_sockets:
				actionable_sockets.remove(sock)
			sock.close()
			sockets.remove(sock)
			del message_queues[sock]
			del command_queues[sock]


def close_client(sock):
	print(f'Lost connection from {sock.getsockname()}.')
	if sock in actionable_sockets:
		actionable_sockets.remove(sock)
	if sock in active_players:
		del active_players[sock]
	sockets.remove(sock)
	del message_queues[sock]
	del command_queues[sock]
	sock.close()