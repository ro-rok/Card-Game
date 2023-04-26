import socket
import random

# Define the server host and port
SERVER_HOST = 'localhost'
SERVER_PORT = 8000

# Define the card suit for this client
SUIT = 'Hearts'

# Define the cards for this client
CARDS = [(1, 'Ace', ''), (2, '2', ''), (3, '3', ''), (4, '4', ''),
         (5, '5', ''), (6, '6', ''), (7, '7', ''), (8, '8', ''), (9, '9', ''),
         (10, '10', ''), (11, 'Jack', ''), (12, 'Queen', ''), (13, 'King', '')]

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the server's host and port
client_socket.connect((SERVER_HOST, SERVER_PORT))

# Send the suit of cards to the server
client_socket.send(SUIT.encode())

# Receive the initial message from the server
data = client_socket.recv(1024).decode()
print(data)

# Prompt regarding game automation
while True:
  try:
    automated = int(
      input(
        "Press 1 for User Card Selection and 2 for Automated Card Selection: ")
    ) - 1
    if automated in [0, 1]:
      break
  except:
    pass


# Function to send the selected card to the server
def send_card(automated, server_card):
  if automated:  # Chooses random card based on server card value
    for card in CARDS:
      if card[1] == server_card:
        card_value = card[0]
    if card_value < 8:
      choice = random.randint(0, 6)
    else:
      choice = random.randint(7, 12)
  else:
    while True:
      try:
        choice = int(input("Select the Card Value to send:")) - 1
        if choice in range(len(CARDS)):
          break
      except:
        pass

  # Send the selected card to the server
  selected_card = CARDS[choice]
  CARDS[choice] = (selected_card[0], selected_card[1],
                   "----------Played----------")
  client_socket.send(f"{selected_card[0]},{selected_card[1]}".encode())


# Loop until the game finishes
for round_num in range(1, 14):

  # Receive the card from the server
  data = client_socket.recv(1024).decode()
  server_card = tuple(data.split(","))
  print(f"Server card: {server_card[0]} of {server_card[1]}")

  # Prompt the user to select a card to send
  for j, card in enumerate(CARDS):
    print(f"{j+1}. {card[1]}  {card[2]}")
  send_card(automated, server_card[0])

  # Receive the winner/error of the round from the server
  while True:
    data = client_socket.recv(1024).decode()  #Round Winner or Error
    error = "You have already used this card. Try Again"  # Server
    if data == error:  # Check if client send the same card
      print(error)
      send_card(automated, server_card[0])
    else:
      print(f"Round {round_num} winner/s: {data}")
      break

# Receive the final message from the server
game_winner = client_socket.recv(1024).decode()
print(f"Game winner: {game_winner}")

# Close the socket
client_socket.close()
