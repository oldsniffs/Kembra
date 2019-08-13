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

Select Usage:
As of now, all outgoing response and observation messages are handled within the readable part of select,
forgoing the use of writables. With more clients connected, using writables might keep socket operations from tripping.
"""

HEADER_LENGTH = 10
VERB_HEADER_LENGTH = 10
CODE_LENGTH = 2
HEADER_AND_CODE = HEADER_LENGTH + 2


server_address = '10.0.0.230'
port = 1234

world_events = []


class Server:
	def __init__(self):
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		self.server.bind((server_address, port))
		self.server.listen(5)

		self.sockets = [self.server]
		self.active_players = {}  # {client socket: player}
		self.broadcasting = []  # sockets with outstanding broadcasts in queue
		self.broadcast_queues = {}  # {socket: Queue} outgoing broadcasts stored in Queue

	def receive_message(self, client_socket):

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
			self.close_client(client_socket)
			return None, None

	def broadcast(self, client_socket, message):
		broadcast_header = f'{len(message):<{HEADER_LENGTH}}'
		print(f'Broadcasting to {client_socket.getsockname()}: {broadcast_header} {message}')
		client_socket.send(broadcast_header.encode('utf-8') + message.encode('utf-8'))

	def queue_broadcast(self, recipient, message):
		self.broadcast_queues[recipient.socket].put(message)
		if recipient.socket not in self.broadcasting:
			self.broadcasting.append(recipient.socket)

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
						code, data = self.receive_message(sock)
					except Exception as e:
						print('Exception reached: ', e)
						self.close_client(sock)
						continue

					if sock not in self.active_players:
						login_name = data
						if not login_name:
							print(f'(From Readable) Lost connection from {sock.getsockname()} during login attempt.')
							self.close_client(sock)

						# Logging in
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
							self.broadcast(sock, f'Welcome to the world, {self.active_players[sock].name}')

					else:
						if code == '01':
							verb = data[:10].strip()
							action = data[10:]
							print(f'Received (verb: action) {verb}: {action}')

							player_action = actions.parse_player_action(self.active_players[sock], verb, action)
							player_action.execute()

						elif code == '00':
							pass

						elif code == '02':
							if data[0] == '\'':
								for s in [s for s in self.sockets if s != self.server]:
									if self.active_players[s].location == self.active_players[sock].location:
										self.broadcast(s, f'{self.active_players[sock].name} says, "{data[1:]}"')
							if data[0] == '!':
								for s in [s for s in self.sockets if s != self.server]:
									if self.active_players[s].location == self.active_players[sock].location:
										self.broadcast(s, f'{self.active_players[sock].name} yells, "{data[1:]}!"')

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
