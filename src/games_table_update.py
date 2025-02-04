from datetime import datetime, timedelta
import sqlite3
import time

from nba_api.stats.endpoints import ScoreboardV2

def create_games_table(cur, con):
    """
    Create the games table if it does not exist already
    
    Parameters:
    cur: Database cursor
    """
    cur.execute('''
        CREATE TABLE IF NOT EXISTS games (
            game_id INTEGER PRIMARY KEY,
            date TEXT
        );
    ''')

    con.commit()

def add_games(cur, con, start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        games_lst = get_game_ids(current_date)
        for game_id in games_lst:
            cur.execute('''
                INSERT OR IGNORE INTO games (game_id, date)
                VALUES (?, ?)
            ''', (game_id, current_date.strftime('%Y-%m-%d')))
            con.commit()
        current_date += timedelta(days=1)

def get_game_ids(current_date):
    """
    Get the game IDs for a given date range
    
    Parameters:
    start_date (datetime): Start date
    end_date (datetime): End date
    """
    print(f"Processing games for {current_date.strftime('%Y-%m-%d')}")
    date_str = current_date.strftime('%m/%d/%Y')
    time.sleep(1)
    scoreboard = ScoreboardV2(game_date=date_str)
    games_df = scoreboard.game_header.get_data_frame()
    return games_df['GAME_ID'].tolist()


def main():
    con = sqlite3.connect('db/games.db')
    cur = con.cursor()

    create_games_table(cur, con)

    # Analyzing the past season of games
    end_date = datetime.now() - timedelta(days=1)
    # 1 day before beginning of NBA 2024/25 season
    start_date = datetime(2024, 10, 21)
    # start_date = datetime.now() - timedelta(days=3)

    add_games(cur, con, start_date, end_date)

    con.close()


