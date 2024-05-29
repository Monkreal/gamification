from otree.api import *
import _templates._python.team as team
import _templates._python.pdf as pdf
import game_nashequilibrium._chart as chart


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'nashequlibrium'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 5
    GAME_NAME = 'Nash Equlibrium'


class Subsession(BaseSubsession):
    nn = models.IntegerField(initial=0)
    np = models.IntegerField(initial=0)
    pn = models.IntegerField(initial=0)
    pp = models.IntegerField(initial=0)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    points = models.IntegerField(initial=0)
    choice = models.BooleanField(initial=False)
        
        
def give_points(subsession):
    players = subsession.get_players()
    
    settings = subsession.session.vars.get('settings', [])    
    
    for team in subsession.session.vars.get('team', []):        
        player1 = [p for p in players if int(p.id_in_group) == int(team[0])][0]
        player2 = [p for p in players if int(p.id_in_group) == int(team[1])][0]        
        
        if player1.choice == False:
            if player2.choice == False:
                player1.points = int(settings[0][0])
                player2.points = int(settings[0][1])
                subsession.nn += 1
            else:
                player1.points = int(settings[1][0])
                player2.points = int(settings[1][1])
                subsession.np += 1
        else:
            if player2.choice == False:
                player1.points = int(settings[2][0])
                player2.points = int(settings[2][1])
                subsession.pn += 1
            else:
                player1.points = int(settings[3][0])
                player2.points = int(settings[3][1])
                subsession.pp += 1
            
        player1.participant.vars['points'] = player1.participant.vars.get('points', 0) + player1.points
        player2.participant.vars['points'] = player2.participant.vars.get('points', 0) + player2.points
    
    
def playerchoice(player):      
    previous = player.in_round(player.subsession.round_number - 1)
    
    settings = player.subsession.session.vars.get('settings', [])
    
    if previous.choice == False:
        return settings[4][0]
    else:
        return settings[4][1]


# PAGES
class settings(Page):
    def is_displayed(self):
        return self.id_in_group == 1 and self.round_number == 1
    
    def live_method(self, data):
        if 'next' in data:
            self.subsession.session.vars['settings'] = data['next']
            
            chart.chart(self.subsession, False)

            return {0: {'next': 'next'}}


class checkin(Page):
    template_name = '_templates/checkin.html'

    def is_displayed(self):
        return not self.subsession.session.vars.get('started', False)
    
    def live_method(self, data):
        if 'next' in data:
            self.subsession.session.vars['started'] = True

            for player in self.subsession.get_players():
                player.participant.vars['notready'] = True
                
            team.create(self.subsession, 2)

            return {0: {'next': 'next'}}

        if 'ready' in data:
            self.participant.vars['checked'] = True
            self.participant.vars['notready'] = False
            self.subsession.session.vars['players'] = self.subsession.session.vars.get('players', 0) + 1
            return {1: {'readyadmin': self.subsession.session.vars.get('players',0)}, self.id_in_group: {'readyplayer': True}}
            

class game(Page):
    def is_displayed(self):
        return (self.participant.vars.get('checked', False) or self.id_in_group == 1) and self.subsession.session.vars.get('adminround', 1) == self.round_number
    
    def vars_for_template(self):        
        template_vars = {}
        settings = self.subsession.session.vars.get('settings', [])
    
        template_vars['negativ'] = settings[4][0]
        template_vars['positiv'] = settings[4][1]
        template_vars['url'] = 'PDF/charts/chart' + str(self.round_number) + '.png'

        if self.round_number != 1 and self.id_in_group != 1:
            teamplayer = team.teamplayer(self)
            
            template_vars['playerchoice'] = playerchoice(self)
            template_vars['teamplayerchoice'] = playerchoice(teamplayer[0])

        return template_vars
    
    def live_method(self, data):
        if 'next' in data:
            for player in self.subsession.get_players():
                player.participant.vars['notready'] = True
                
            self.subsession.session.vars['ready'] = 0
            
            self.subsession.session.vars['adminround'] = self.subsession.session.vars.get('adminround', 1) + 1
            
            give_points(self.subsession)
            
            chart.chart(self.subsession, True, self.round_number)
            
            return {0: {'next': 'next'}}

        if 'choice' in data:
            self.subsession.session.vars['ready'] = self.subsession.session.vars.get('ready', 0) + 1
            self.participant.vars['notready'] = False
            
            if data['choice'] == 'True':
                self.choice = True
            else:
                self.choice = False
                
            return {1: {'readyadmin': self.subsession.session.vars.get('ready', 0)}, self.id_in_group: {'readyplayer': True}}
            

class result(Page):
    template_name = '_templates/result.html'

    def is_displayed(self):
        return self.round_number == C.NUM_ROUNDS
    
    def vars_for_template(player):
        urls = []
        
        for round in range(C.NUM_ROUNDS):
            urls.append([round + 1, 'PDF/charts/chart' + str(round + 2) + '.png'])
            
        return dict(
            urls = urls
        )
        
    def live_method(self, data):
        if 'next' in data:
            urls = []
        
            for round in range(C.NUM_ROUNDS):
                urls.append('_static/PDF/charts/chart' + str(round + 2) + '.png')
            
            pdf.create_pdf(urls, C.GAME_NAME, self.subsession.get_players())
            
            return {1: {'PDF': 'PDF'}}


page_sequence = [settings, checkin, game, result]
