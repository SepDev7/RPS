from sqlalchemy.orm import Session
from sqlalchemy import select
from with_solid import PlayerRecord, GameRecord, LeaderboardRecord, engine

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

def display_leaderboard():
    session = Session(engine)
    leaderboard_entries = session.execute(select(LeaderboardRecord)).scalars().all()
    print("Leaderboard:")
    for entry in leaderboard_entries:
        player = session.query(PlayerRecord).filter(PlayerRecord.id == entry.player_id).first()
        print(f"Player ID: {entry.player_id}, Name: {player.name}, Score: {entry.score}")
    session.close()

if __name__ == "__main__":
    display_players()
    display_games()
    display_leaderboard()
