from nba_api.stats.static import players
from nba_api.stats.static import teams

def get_active_player_dict():
    """
    Return a dictionary of all active players
    """
    return {p['id']: p['full_name'] for p in players.get_players() if p['is_active']}

def get_team_id(name: str) -> int:
    nba_teams = teams.get_teams()
    for team in nba_teams:
        if team['nickname'] == name:
            return team['id']

def get_player_id(name: str) -> int:
    nba_players = players.get_players()
    for player in nba_players:
        if player['full_name'] == name:
            return player['id']