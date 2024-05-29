from otree.api import *
import _templates._python.pdf as pdf
import game_publicgood._chart as chart


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'gamename'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 5
    GAME_NAME = 'Game Name'


class Subsession(BaseSubsession):
    pass


#Dont use this
class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass
        
#Place for your functions
            
            
# PAGES
class settings(Page):
    def is_displayed(self):
        return self.id_in_group == 1 and self.round_number == 1
    
    def live_method(self, data):
        if 'next' in data:
            #Place for settings function

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
                
            #Place for function after Players are clear

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
        #Place for function
        return {
            #Place for game Variables
        }
    
    def live_method(self, data):
        if 'next' in data:
            for player in self.subsession.get_players():
                player.participant.vars['notready'] = True
                
            self.subsession.session.vars['ready'] = 0
            
            self.subsession.session.vars['adminround'] = self.subsession.session.vars.get('adminround', 1) + 1
            
            #Place for your functions
            
            if self.round_number == C.NUM_ROUNDS:
                chart.create(self.subsession, C.NUM_ROUNDS)
            
            return {0: {'next': 'next'}}
            
        # here you can handel Player interaction
            

class result(Page):
    template_name = '_templates/result.html'

    def is_displayed(self):
        return self.round_number == C.NUM_ROUNDS
    
    
    def vars_for_template(self):
        #here you can Place some function
        return dict(
            #infos for Pictures you wan't to show on the Page
            urls = [[1, 'PDF/charts/chart.png']]
        )
        
    def live_method(self, data):
        if 'next' in data:
            pdf.create_pdf(['_static/PDF/charts/chart.png'], C.GAME_NAME, self.subsession.get_players())
            
            return {1: {'PDF': 'PDF'}}


page_sequence = [settings, checkin, game, result]