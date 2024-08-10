import socket
import pickle

class GameClient:
    def __init__(self, host='localhost', port=12345):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

    def send_name(self):
        player_name = input("Enter your name: ")
        self.client.send(pickle.dumps(player_name))

    def play(self):
        self.send_name()

        while True:
            message = pickle.loads(self.client.recv(1024))
            print(message)

            if "Your move" in message:
                move = input("Enter your move (rock, paper, scissors): ")
                self.client.send(pickle.dumps(move))
            elif "Do you want to play another round?" in message:
                response = input("Do you want to play another round? (yes/no): ")
                self.client.send(pickle.dumps(response))
            elif "Game Over!" in message:
                print("Game Over! Thanks for playing.")
                break
            else:
                print(message)

if __name__ == "__main__":
    client = GameClient()
    client.play()
