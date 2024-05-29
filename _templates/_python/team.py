def create(subsession, size):    
    players = subsession.get_players()

    players_checked = [p for p in players if p.participant.vars.get('checked', False) and not p.id_in_group == 1]
    
    team = []

    while len(players_checked) >= size:
        player1 = players_checked.pop(0)
        player2 = players_checked.pop(0)
        
        team.append([player1.id_in_group, player2.id_in_group])
        
    subsession.session.vars['team'] = team

    if len(players_checked) != 0:
        for player in players_checked:
            player.participant.vars['checked'] = False
            
def teamplayer(player):
    id = player.id_in_group
    
    teams = player.subsession.session.vars.get('team', [])
    
    team = [t for t in teams if id in t][0]
    
    players = player.subsession.get_players()
    
    return [p for p in players if p.id_in_group in team and p.id_in_group != id]