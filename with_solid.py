from abc import ABC, abstractmethod
from typing import Optional, Dict
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship

# SQLAlchemy setup
DATABASE_URL = "postgresql://postgres:admin@localhost:5433/rockpaperscissors"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PlayerRecord(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
class GameRecord(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    player1_id = Column(Integer, ForeignKey("players.id"))
    player2_id = Column(Integer, ForeignKey("players.id"))
    winner_id = Column(Integer, ForeignKey("players.id"))
    
    player1 = relationship("PlayerRecord", foreign_keys=[player1_id])
    player2 = relationship("PlayerRecord", foreign_keys=[player2_id])
    winner = relationship("PlayerRecord", foreign_keys=[winner_id])

class LeaderboardRecord(Base):
    __tablename__ = "leaderboard"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), unique=True)
    score = Column(Integer, default=0)

    player = relationship("PlayerRecord")

Base.metadata.create_all(bind=engine)

class Player(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get_choice(self) -> str:
        pass

class HumanPlayer(Player):
    def get_choice(self) -> str:
        choice = input(f"{self.name}, enter your choice (rock, paper, scissors): ").lower()
        while choice not in ["rock", "paper", "scissors"]:
            print("Invalid choice. Please try again.")
            choice = input(f"{self.name}, enter your choice (rock, paper, scissors): ").lower()
        return choice

class GameRules:
    @staticmethod
    def determine_winner(choice1: str, choice2: str) -> Optional[int]:
        if choice1 == choice2:
            return None
        elif (choice1 == "rock" and choice2 == "scissors") or \
             (choice1 == "scissors" and choice2 == "paper") or \
             (choice1 == "paper" and choice2 == "rock"):
            return 1
        else:
            return 2

class Game:
    def __init__(self, player1: Player, player2: Player):
        self.player1 = player1
        self.player2 = player2
        self.player1_score = 0
        self.player2_score = 0

    def play_round(self):
        choice1 = self.player1.get_choice()
        choice2 = self.player2.get_choice()
        winner = GameRules.determine_winner(choice1, choice2)
        if winner == 1:
            self.player1_score += 1
            print(f"{self.player1.name} wins this round!")
        elif winner == 2:
            self.player2_score += 1
            print(f"{self.player2.name} wins this round!")
        else:
            print("This round is a tie!")

    def play(self):
        while True:
            self.play_round()
            another_round = input("Do you want to play another round? (yes/no): ").lower()
            if another_round != 'yes':
                break
        print(f"Final Score - {self.player1.name}: {self.player1_score}, {self.player2.name}: {self.player2_score}")
        if self.player1_score > self.player2_score:
            print(f"{self.player1.name} wins the session!")
            return self.player1.name
        elif self.player2_score > self.player1_score:
            print(f"{self.player2.name} wins the session!")
            return self.player2.name
        else:
            print("The session is a tie!")
            return None

class Leaderboard:
    def __init__(self):
        self.scores: Dict[str, int] = {}

    def update(self, winner_name: Optional[str]):
        if winner_name:
            if winner_name in self.scores:
                self.scores[winner_name] += 1
            else:
                self.scores[winner_name] = 1

    def display(self):
        print("\nLeaderboard:")
        for player, score in sorted(self.scores.items(), key=lambda x: x[1], reverse=True):
            print(f"{player}: {score} points")

class RockPaperScissorsGame:
    def __init__(self):
        self.leaderboard = Leaderboard()
        self.db = SessionLocal()

    def get_or_create_player(self, name: str) -> PlayerRecord:
        player = self.db.query(PlayerRecord).filter(PlayerRecord.name == name).first()
        if not player:
            player = PlayerRecord(name=name)
            self.db.add(player)
            self.db.commit()
            self.db.refresh(player)
        return player

    def start(self):
        while True:
            print("\nNew Game Session")
            player1_name = input("Enter the name of Player 1: ")
            player2_name = input("Enter the name of Player 2: ")
            player1 = HumanPlayer(player1_name)
            player2 = HumanPlayer(player2_name)

            player1_record = self.get_or_create_player(player1_name)
            player2_record = self.get_or_create_player(player2_name)

            game = Game(player1, player2)
            winner_name = game.play()

            if winner_name:
                winner_record = self.get_or_create_player(winner_name)
            else:
                winner_record = None

            game_record = GameRecord(
                player1_id=player1_record.id,
                player2_id=player2_record.id,
                winner_id=winner_record.id if winner_record else None
            )
            self.db.add(game_record)
            self.db.commit()

            self.leaderboard.update(winner_name)
            self.leaderboard.display()

            new_session = input("Do you want to start a new session? (yes/no): ").lower()
            if new_session != 'yes':
                break

if __name__ == "__main__":
    RockPaperScissorsGame().start()
