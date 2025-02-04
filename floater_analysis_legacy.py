from nba_api.stats.endpoints import PlayByPlayV3, ScoreboardV2, LeagueDashPlayerStats
from nba_api.stats.static import players
from datetime import datetime, timedelta
import pandas as pd
import time
from collections import defaultdict

class FloaterAnalyzer:
    def __init__(self, start_date=None, end_date=None):
        """
        Initialize the analyzer with date range for analysis.
        
        Parameters:
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format
        """
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        self.floater_stats = defaultdict(lambda: {'attempted': 0, 'made': 0, 'points': 0, 'gp': 0})
        self.active_players = {p['id']: p['full_name'] for p in players.get_players() 
                             if p['is_active']}
        self.errors = 0

    def get_game_ids(self, date):
        """
        Get all game IDs for a specific date.
        
        Parameters:
        date (datetime): Date to get games for
        
        Returns:
        list: List of game IDs
        """
        date_str = date.strftime('%m/%d/%Y')
        time.sleep(1) # Respect API rate limits
        scoreboard = ScoreboardV2(game_date=date_str)
        games_df = scoreboard.game_header.get_data_frame()
        return games_df['GAME_ID'].tolist()

    def add_games_played(self, player_id, stats):
        """
        Add the number of games played for each player.
        
        Parameters:
        player_id (int): Player ID
        """
        df = stats.get_data_frames()[0]

        player_stats = df[df['PLAYER_ID'] == player_id]

        if len(player_stats) == 0:
            self.floater_stats[player_id]['gp'] = 0
        else:
            self.floater_stats[player_id]['gp'] = int(player_stats['GP'].iloc[0])


    def add_floaters(self, game_id, stats):
        """
        Analyze play-by-play data for a specific game to find floaters
        
        Parameters:
        game_id (str): NBA game ID
        """

        try:
            time.sleep(1)  # Respect API rate limits
            pbp = PlayByPlayV3(game_id=game_id)
            plays_df = pbp.get_data_frames()[0]
            
            # Filter for floaters
            floater_plays = plays_df[
                plays_df['description'].str.contains('float', na=False, case=False) &
                plays_df['isFieldGoal'].astype(int) == 1
            ]
            
            # Process each floater
            for _, play in floater_plays.iterrows():
                # Extract player ID from the play description
                if play['personId'] in self.active_players:
                    player_id = play['personId']
                    self.add_games_played(player_id, stats)
                    self.floater_stats[player_id]['attempted'] += 1
                    if play['shotResult'] == 'Made':
                        self.floater_stats[player_id]['made'] += 1
                        self.floater_stats[player_id]['points'] += play['shotValue']
            
        except Exception as e:
            print(f"Error processing game {game_id}: {str(e)}")
            self.errors += 1

    def analyze_date_range(self, stats):
        """
        Analyze all games within the specified date range.
        """
        current_date = self.start_date
        while current_date <= self.end_date:
            print(f"Processing games for {current_date.strftime('%Y-%m-%d')}...")
            game_ids = self.get_game_ids(current_date)
            
            for game_id in game_ids:
                self.add_floaters(game_id, stats)
            
            current_date += timedelta(days=1)

    def get_results(self):
        """
        Get analyzed results in a pandas DataFrame.
        
        Returns:
        pandas.DataFrame: floater statistics for all players
        """
        results = []
        for player_id, stats in self.floater_stats.items():
            results.append({
                'Player': self.active_players[player_id],
                'Floaters Attempted': stats['attempted'],
                'Floaters Made': stats['made'],
                'Floaters Attempted Per Game': round(stats['attempted'] / stats['gp'], 2),
                'Floaters Made Per Game': round(stats['made'] / stats['gp'], 2),
                'Floater Percentage': round((stats['made'] / stats['attempted'])*100, 2)
            })
        
        df = pd.DataFrame(results)
        return df.sort_values('Floaters Made Per Game', ascending=False)

def analyze_floaters(start_date, end_date):
    """
    Analyze floaters for a specific date range.
    
    Parameters:
    start_date (str): Start date in 'YYYY-MM-DD' format
    end_date (str): End date in 'YYYY-MM-DD' format
    """
    try:
        print(f"\nAnalyzing floaters from {start_date} to {end_date}")
        print("This may take some time due to API rate limits...")
        
        stats = LeagueDashPlayerStats(season='2024-25')

        analyzer = FloaterAnalyzer(start_date, end_date)

        analyzer.analyze_date_range(stats)

        results = analyzer.get_results()

        print(f"\nAnalysis complete!")
        if analyzer.errors > 0:
            print(f"{analyzer.errors} game(s) had errors and will not be included in analysis")

        print('Writing to CSV file...')
        results.to_csv('floater_analysis.csv', index=False)

        print("\nNBA Players - Floater Statistics")
        print("-" * 80)
        print(results.head(25).to_string(index=False))
        
        return results
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please check your internet connection and NBA API package installation.")

if __name__ == "__main__":
    # Example usage: Analyze the past season
    end_date = datetime.now() - timedelta(days=1)
    # Beginning of NBA 2024/25 season
    start_date = datetime(2024, 10, 22)
    # start_date = end_date - timedelta(days=3)

    start = time.time()

    analyze_floaters(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )

    end = time.time()

    print(f"Floater Analysis took {end-start} seconds to complete")