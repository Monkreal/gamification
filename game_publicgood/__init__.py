from otree.api import *
import _templates._python.pdf as pdf
import game_publicgood._chart as chart


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'publicgood'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 5
    GAME_NAME = 'Public Good'


class Subsession(BaseSubsession):
    publicgood = models.IntegerField(initial=0)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    points = models.IntegerField()
    pay = models.IntegerField()
        

def give_start_points(subsession, points_admin):
    for player in subsession.get_players():
        if not player.id_in_group == 1:
            player.participant.vars['points'] = int(points_admin)

        
def give_points(subsession):
    if subsession.publicgood != 0:
        extra_points = int((subsession.publicgood * 1.5) / subsession.session.vars.get('players', 0))
    else:
        extra_points = 0
    
    for player in subsession.get_players():
        if not(player.participant.vars.get('admin', False)) and player.participant.vars.get('checked', False):
            player.points = player.participant.vars.get('points', 0)
            player.participant.vars['points'] = int(player.points - player.pay + extra_points)
            
            
# PAGES
class settings(Page):
    def is_displayed(self):
        return self.id_in_group == 1 and self.round_number == 1
    
    def live_method(self, data):
        if 'next' in data:
            give_start_points(self.subsession, data['vermoegen'])

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

            return {0: {'next': 'next'}}

        if 'ready' in data:
            self.participant.vars['checked'] = True
            self.participant.vars['notready'] = False
            self.subsession.session.vars['players'] = self.subsession.session.vars.get('players', 0) + 1
            return {1: {'readyadmin': self.subsession.session.vars.get('players', 0)}, self.id_in_group: {'readyplayer': True}}
            

class game(Page):
    def is_displayed(self):
        return (self.participant.vars.get('checked', False) or self.id_in_group == 1) and self.subsession.session.vars.get('adminround', 1) == self.round_number
    
    def vars_for_template(self):
        return {
            'subsession1': self.subsession.in_round(1),
            'subsession2': self.subsession.in_round(2),
            'subsession3': self.subsession.in_round(3),
            'subsession4': self.subsession.in_round(4),
            'subsession5': self.subsession.in_round(5),
        }
    
    def live_method(self, data):
        if 'next' in data:
            for player in self.subsession.get_players():
                player.participant.vars['notready'] = True
                
            self.subsession.session.vars['ready'] = 0
            
            self.subsession.session.vars['adminround'] = self.subsession.session.vars.get('adminround', 1) + 1
            
            give_points(self.subsession)
            
            if self.round_number == C.NUM_ROUNDS:
                chart.create(self.subsession, C.NUM_ROUNDS)
            
            return {0: {'next': 'next'}}
            
        if 'choice' in data:
            try:
            
                if self.participant.vars.get('points', 0) - int(data['choice']) >= 0 and int(data['choice']) >= 0:
            
                    self.pay = int(data['choice'])
                    self.subsession.publicgood += int(data['choice'])
                    
                    self.participant.vars['notready'] = False
                    self.subsession.session.vars['ready'] = self.subsession.session.vars.get('ready', 0) + 1
                
                    return {1: {'readyadmin': self.subsession.session.vars.get('ready', 0)}, self.id_in_group: {'readyplayer': True}}
            
                else:
                    return {self.id_in_group: {'error': 'die Eingabe ist ungültig'}}
            
            except ValueError:
                return {self.id_in_group: {'error': 'die Eingabe ist ungültig'}}
            

class result(Page):
    template_name = '_templates/result.html'

    def is_displayed(self):
        return self.round_number == C.NUM_ROUNDS
    
    
    def vars_for_template(self):
        return dict(
            urls = [[1, 'PDF/charts/chart.png']]
        )
        
    def live_method(self, data):
        if 'next' in data:
            pdf.create_pdf(['_static/PDF/charts/chart.png'], C.GAME_NAME, self.subsession.get_players())
            
            return {1: {'PDF': 'PDF'}}


page_sequence = [settings, checkin, game, result]
