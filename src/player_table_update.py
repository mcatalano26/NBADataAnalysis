import sqlite3

from nba_api.stats.endpoints import LeagueDashPlayerStats
from util.utils import get_active_player_dict

def create_player_table(cur):
    """
    Create the players table if it does not exist already
    
    Parameters:
    cur: Database cursor
    """
    cur.execute('''
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY,
            player_name TEXT,
            gp INTEGER
        )
    ''')

def add_games_played(player_id, stats, cur, con, active_players_dct):
    """
    Add the number of games played for each player to the players database
    
    Parameters:
    player_id (int): Player ID
    stats: LeagueDashPlayerStats object
    """
    try:
        df = stats.get_data_frames()[0]

        player_stats = df[df['PLAYER_ID'] == player_id]

        if len(player_stats) > 0:
            values = (player_id, player_stats['PLAYER_NAME'].iloc[0], int(player_stats['GP'].iloc[0]))

            cur.execute('''
                INSERT OR REPLACE INTO players (player_id, player_name, gp)
                VALUES (?, ?, ?)
            ''', values)
            con.commit()
    except Exception as e:
        print(f"Error processing player {player_id} - {active_players_dct[player_id]}: {e}")



def main():
    con = sqlite3.connect('db/players.db')
    cur = con.cursor()

    active_players_dct = get_active_player_dict()

    create_player_table(cur)

    stats = LeagueDashPlayerStats(season='2024-25')

    for player_id in active_players_dct:
        add_games_played(player_id, stats, cur, con, active_players_dct)

    con.commit()
    con.close()





