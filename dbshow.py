from sqlalchemy.orm import Session
from sqlalchemy import select

# Assuming PlayerRecord and GameRecord are already defined as per the previous code
from with_solid import PlayerRecord, GameRecord, engine  # Replace 'your_module' with the actual module name

def display_players():
    session = Session(engine)
    players = session.execute(select(PlayerRecord)).scalars().all()
    print("Players:")
    for player in players:
        print(f"ID: {player.id}, Name: {player.name}")
    session.close()

def display_games():
    session = Session(engine)
    games = session.execute(select(GameRecord)).scalars().all()
    print("Games:")
    for game in games:
        print(f"ID: {game.id}, Player1 ID: {game.player1_id}, Player2 ID: {game.player2_id}, Winner ID: {game.winner_id}")
    session.close()

if __name__ == "__main__":
    display_players()
    display_games()
