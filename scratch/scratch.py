import sqlite3

from nba_api.stats.endpoints import PlayByPlayV3

# You can use game_id + actionId from the PlayByPlayV3 dataframe to get a unique ID for the table
# pbp = PlayByPlayV3(game_id='0022300350')
# plays_df = pbp.get_data_frames()[0]
# print(plays_df['actionId'].nunique())
# print(len(plays_df.index))

con = sqlite3.connect('db/games.db')
cur = con.cursor()

cur.execute('SELECT * FROM games WHERE date = "2025-02-01"')
rows = cur.fetchall()
count = 0
for row in rows:
    print(row)
    count += 1

print(f"Total games: {count}")