#python -m pip install tabulate """ TO DOWNLOAD THE TABLE LIB"""

import random
import socket
from tabulate import tabulate

# Create a map to store the client scores
client_scores = {"Client 1": 0, "Client 2": 0, "Client 3": 0}

#Create Contents for table
table = [["0 (Intialization)", 0, 0, 0]]
headers = ["Rounds", "Client 1 Score", "Client 2 Score", "Client 3 Score"]

# Create a map To id the client
client_id = {}

# Define the card suit for the server
suits = 'Spades'

# Definestore cards for the server
card_list = [(1, 'Ace'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'),
             (7, '7'), (8, '8'), (9, '9'), (10, '10'), (11, 'Jack'),
             (12, 'Queen'), (13, 'King')]

used_server = set()

# Create a map to store the used card
used_client = {"Client 1": [], "Client 2": [], "Client 3": []}


# Define a function to get a random card from the server suit
def draw_card():
  while True:
    random_number = random.randint(0, 12)
    card = (card_list[random_number][0], suits, card_list[random_number][1])
    if card not in used_server:
      used_server.add(card)
      return card


# Define a function to receive a card from a client
def receive_card(conn):
  while True:
    data = conn.recv(1024).decode()
    card = tuple(data.split(","))
    #To check if the recieved card is already played or not
    if card not in used_client[client_id[conn.getpeername()]]:
      used_client[client_id[conn.getpeername()]].append(card)
      return card
    else:
      # Sending the error to the client to send the code again
      error = "You have already used this card. Try Again"
      conn.send(f"{error}".encode())
      new_card = receive_card(conn)
      return new_card


# Set up the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 8000))

# Start listening for incoming connections
print("Server is listening for incoming connections...")
server_socket.listen()

# Accept 3 client connections and map their id
client_conns = []
for i in range(3):
  conn, addr = server_socket.accept()
  client_conns.append(conn)
  client_id[conn.getpeername()] = "Client " + str(i + 1)
  print(f"Client {i+1} connected from {addr}")

# Get the suit for each client
suit_client = {}
for conn in client_conns:
  suit = conn.recv(1024).decode()
  suit_client[client_id[conn.getpeername()]] = suit
  print(f"{client_id[conn.getpeername()]} chose suit {suit}")

# Welcoming the players to the game
welcome = "Let's play the game"
for conn in client_conns:
  conn.sendall(f"{welcome}".encode())

# Play 13 rounds of the game
for round_num in range(1, 14):
  print(f"Round {round_num}:")

  # Get a card from the server suit
  server_card = draw_card()
  print(f"The server advertised card {server_card[2]} of {server_card[1]}")

  # Send the server card to each client
  for conn in client_conns:
    conn.sendall(f"{server_card[2]}, {server_card[1]}".encode())

  # Receive a card from each client
  client_cards = []
  for conn in client_conns:
    card = receive_card(conn)
    client_cards.append(card)
    print(
      f"{client_id[conn.getpeername()]} sent card {card[1]} of {suit_client[client_id[conn.getpeername()]]}"
    )

  # Determine the winning card and client
  winning_card = max(client_cards, key=lambda x: int(x[0]))
  winning_clients = [
    i + 1 for i, card in enumerate(client_cards) if card == winning_card
  ]

  # Increment the scores of the winning clients
  for client in winning_clients:
    client_name = f"Client {client}"
    client_scores[client_name] += server_card[0]

  # Print the winner(s) of the round and increment their scores
  if len(winning_clients) == 1:
    winner_string = ", ".join(
      [client_id[client_conns[i - 1].getpeername()] for i in winning_clients])
    print(
      f"Winner of the round: {winner_string} (since it sent the highest value card among all clients)"
    )
  elif len(winning_clients) == 2:
    winner_string = ", ".join(
      [client_id[client_conns[i - 1].getpeername()] for i in winning_clients])
    print(
      f"Winner of the round: {winner_string} (since both {winner_string} sent the winning card)"
    )
  else:
    winner_string = ", ".join(
      [client_id[client_conns[i - 1].getpeername()] for i in winning_clients])
    print(
      f"Winner of the round: {winner_string} (since all clients sent the winning card)"
    )

  print(f"Server increments the points of {winner_string} by {server_card[0]}")

  # Sending the winners of the round
  for conn in client_conns:
    conn.sendall(f"{winner_string}".encode())

  # Print the score
  table.append([round_num] + list(client_scores.values()))
  print("Current scores:")
  for client_name, score in client_scores.items():
    print(f"{client_name}: {score}")

print(tabulate(table, headers, tablefmt="pretty"))

# Advertise the winner to all clients
winner = gamewinner_string = ", ".join([
  key for key, value in client_scores.items()
  if value == max(client_scores.values())
])
print(f"Winner of the game: {winner}")
for conn in client_conns:
  conn.sendall(f"The winner is {winner}".encode())

# Close the connections
for conn in client_conns:
  conn.close()
server_socket.close()