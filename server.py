import socket
import threading
import pickle
from sqlalchemy.orm import sessionmaker
from with_solid import PlayerRecord, GameRecord, LeaderboardRecord, engine, Base, GameRules

# SQLAlchemy setup
SessionLocal = sessionmaker(bind=engine)

class GameServer:
    def __init__(self, host='localhost', port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        print(f"Server listening on {host}:{port}")
        self.clients = {}  # {client_socket: player_name}
        self.moves = {}  # {player_name: move}
        self.session = SessionLocal()

    def handle_client(self, client_socket):
        try:
            player_name = pickle.loads(client_socket.recv(1024))
            self.clients[client_socket] = player_name
            print(f"{player_name} has joined the game.")

            # Wait until both players have joined
            if len(self.clients) == 2:
                # Notify both players that the game is starting
                self.broadcast("Game is starting!")
                self.start_game()
            else:
                client_socket.send(pickle.dumps("Waiting for another player..."))

        except Exception as e:
            print(f"Error handling client: {e}")
            client_socket.close()

    def broadcast(self, message, exclude_socket=None):
        for client in self.clients:
            if client != exclude_socket:
                client.send(pickle.dumps(message))

    def start_game(self):
        while True:
            for client_socket in self.clients:
                player_name = self.clients[client_socket]
                client_socket.send(pickle.dumps("Your move (rock, paper, scissors):"))
                move = pickle.loads(client_socket.recv(1024))
                self.moves[player_name] = move
                print(f"{player_name} has chosen {move}")

            if len(self.moves) == 2:
                self.determine_winner()
                self.moves.clear()

                # Ask if they want to play another round
                continue_game = self.ask_to_continue()
                if not continue_game:
                    self.broadcast("Game Over!")
                    break

    def determine_winner(self):
        player1, player2 = list(self.moves.keys())
        move1, move2 = self.moves[player1], self.moves[player2]
        winner = GameRules.determine_winner(move1, move2)

        if winner == 1:
            result = f"{player1} wins with {move1} over {move2}!"
        elif winner == 2:
            result = f"{player2} wins with {move2} over {move1}!"
        else:
            result = "It's a tie!"

        print(result)
        self.broadcast(result)

    def ask_to_continue(self):
        continue_responses = []
        for client_socket in self.clients:
            client_socket.send(pickle.dumps("Do you want to play another round? (yes/no)"))
            response = pickle.loads(client_socket.recv(1024))
            continue_responses.append(response.lower())

        # If both players want to continue, return True, else return False
        return all(resp == 'yes' for resp in continue_responses)

    def start(self):
        while True:
            client_socket, addr = self.server.accept()
            print(f"Connection from {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    GameServer().start()
