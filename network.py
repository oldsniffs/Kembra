import select
import socket
import queue
import pickle
import time

import people
import actions

"""Questions

How much exception catching do I need through the recieve methods?
They have yet to raise in testing, but will the server crash if they do?
Basically, I currently don't have the experience/knowledge to know how to implement it

"""

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

Select Usage:
As of now, all outgoing response and observation messages are handled within the readable part of select,
forgoing the use of writables. With more clients connected, using writables might keep socket operations from tripping.
"""

HEADER_LENGTH = 10
VERB_HEADER_LENGTH = 10
CODE_LENGTH = 2
HEADER_AND_CODE = HEADER_LENGTH + 2


server_address = '10.0.0.121'
port = 4400

world_events = []


class Server:  # Game server would be better class name, to distinguish from the server attribute
	def __init__(self):
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		self.server.bind((server_address, port))
		self.server.listen(5)

		self.sockets = [self.server]
		self.active_players = {}  # {client socket: player}
		self.broadcasting = []  # sockets with outstanding broadcasts in queue
		self.broadcast_queues = {}  # {socket: Queue} outgoing broadcasts stored in Queue

	def receive_code(self, client_socket):

		try:
			code = client_socket.recv(CODE_LENGTH).decode('utf-8')
			return code

		except ConnectionResetError as e:
			self.close_client(client_socket)

	def receive_login(self, client_socket):

		client_socket.settimeout(.1)
		try:

			header = client_socket.recv(HEADER_LENGTH).decode('utf-8')

			if not len(header):
				raise Exception

			message_length = int(header)
			message = client_socket.recv(message_length).decode('utf-8')

			return message

		except ConnectionResetError as e:
			print(f'ConnectionResetError from {client_socket.getsockname()}: {e}')
			self.close_client(client_socket)
			return None, None

	def receive_command(self, client_socket):

		action_command = client_socket.recv(4096)
		return pickle.loads(action_command)

	def broadcast(self, client_socket, message):

		broadcast_header = f'{len(message):<{HEADER_LENGTH}}'
		print(f'Broadcasting to {client_socket.getsockname()}: {broadcast_header} {message}')
		client_socket.send(broadcast_header.encode('utf-8') + message.encode('utf-8'))

	def queue_broadcast(self, recipient, message):

		self.broadcast_queues[recipient.socket].put(message)
		if recipient.socket not in self.broadcasting:
			self.broadcasting.append(recipient.socket)

		print(f'server.queue_broadcast of message: {message} complete! -- {recipient.world.clock.now()}')

	def run_server(self, world):
		print('Server online: Accepting connections...')
		while True:
			readable, writable, exceptional = select.select(self.sockets, self.broadcasting, self.sockets)
			# possible renames: readable -> incoming, writable -> outgoing

			for sock in readable:
				if sock == self.server:

					new_client, client_address = self.server.accept()
					new_client.setblocking(False)
					print(f'Connection from {client_address[0]}:{client_address[1]} established')
					self.sockets.append(new_client)
					self.broadcast_queues[new_client] = queue.Queue()

				elif sock in self.sockets:
					try:
						code = self.receive_code(sock)
					except Exception as e:
						print('Exception reached: ', e)
						self.close_client(sock)
						continue

					if code == '00' and sock not in self.active_players: # '00' can be used other than login, so both conditions here is ok
						login_name = self.receive_login(sock)
						if not login_name:
							self.close_client(sock)

						# Logging in
						# Login sequence needs more granular structure
						if login_name in [player.name for player in world.players]:
							for player in world.players:
								if login_name == player.name:
									player.socket = sock
									self.active_players[sock] = player
									print(f'{sock.getsockname} logged in as {self.active_players[sock].name}')
									self.broadcast(sock, f'Logged in as {self.active_players[sock].name}. Welcome back.')
						else:
							self.active_players[sock] = people.Player(world, login_name)
							self.broadcast_queues[sock] = queue.Queue()
							self.active_players[sock].server = self
							self.active_players[sock].socket = sock
							print(f'New player {login_name} created by {sock.getsockname()}')
							world.players.append(self.active_players[sock])
							world.active_players.append(self.active_players[sock])
							# world.high_priority_timers[self.active_players[sock]] = queue.Queue()
							self.broadcast(sock, f'Welcome to the world, {self.active_players[sock].name}')

					elif code == '01':
						# Get command, validate it, send into central loop

						player_command = self.receive_command(sock)

						player_action = actions.Action(self, self.active_players[sock], player_command.verb, player_command.target, player_command.quantity)
						self.active_players[sock].current_action = player_action

			for sock in writable:
				try:
					message = self.broadcast_queues[sock].get_nowait()
				except queue.Empty:
					self.broadcasting.remove(sock)
				else:
					self.broadcast(sock, message)

			for sock in exceptional:
				print(f'(From exceptional list) Lost connection from {sock.getsockname()}.')
				self.close_client(sock)

	def close_client(self, sock):
		print(f'Lost connection from {sock.getsockname()}.')
		self.active_players[sock].sock = None
		if sock in self.broadcasting:
			self.broadcasting.remove(sock)
		if sock in self.active_players:
			del self.active_players[sock]
		self.sockets.remove(sock)
		del self.broadcast_queues[sock]
		sock.close()
