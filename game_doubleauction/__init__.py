from otree.api import *

import random
import game_doubleauction._chart as chart
import _templates._python.pdf as pdf


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'doubleauction'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 5
    GAME_NAME = 'Double Auction'


class Subsession(BaseSubsession):
    average = models.IntegerField()


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    seller = models.BooleanField(initial=False)
    cost = models.IntegerField()
    offer = models.IntegerField()
    deal = models.IntegerField()

        
def give_cost(subsession):
    cost_buyer = []
    cost_seller = []
    
    count = 1
    countbuyer = 1
    countseller = 1
    
    for player in subsession.get_players():
        if player.participant.vars.get('checked', False) and not player.id_in_group == 1:
            if count % 2 == 0:
                cost_buyer.append(countbuyer * 10 + 20)
                countbuyer += 1
            else:
                cost_seller.append(countseller * 10)
                countseller += 1
            count += 1
    
    count = 1
    
    subsession.session.vars['buyercount'] = len(cost_buyer)
    subsession.session.vars['sellercount'] = len(cost_seller)
            
    cost_buyer_lists = [list(cost_buyer) for _ in range(C.NUM_ROUNDS)]
    cost_seller_lists = [list(cost_seller) for _ in range(C.NUM_ROUNDS)]
      
    for player in subsession.get_players():
        if player.participant.vars.get('checked', False) and not player.id_in_group == 1:
            player_costs = cost_seller_lists if count % 2 else cost_buyer_lists
        
            for round_number in range(C.NUM_ROUNDS):
                round_costs = player_costs[round_number]
            
                if round_costs:
                    irandom = random.randint(0, len(round_costs) - 1)
                    p = player.in_round(round_number + 1)
                    p.cost = round_costs.pop(irandom)
                    
                    if count % 2:
                        p.seller = True
                    else:
                        p.seller = False
                else:
                    p.cost = None
        
            count += 1
            
            
def get_offer_list(subsession, seller):
    offer_list = []
    
    for player in subsession.get_players():
        deal = player.field_maybe_none('deal')
        offer = player.field_maybe_none('offer')
        
        if player.seller == seller and deal is None and not offer is None:
            offer_list.append([player.id_in_group, player.offer])
    
    if seller:                
        offer_list = sorted(offer_list, key=lambda x: x[1])
    else:
        offer_list = sorted(offer_list, key=lambda x: x[1], reverse=True)   
        
    if len(offer_list) > 5:
        offer_list = offer_list[:5]
    else:
        while len(offer_list) < 5:
            offer_list.append(["",""])
            
    return offer_list
            
            
# PAGES

class checkin(Page):
    template_name = '_templates/checkin.html'
    
    def is_displayed(self):
        return not self.subsession.session.vars.get('started', False)
    
    def live_method(self, data):
        if 'next' in data:
            self.subsession.session.vars['started'] = True

            for player in self.subsession.get_players():
                player.participant.vars['notready'] = True
                
            give_cost(self.subsession)

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
        seller_list = get_offer_list(self.subsession, True)
        buyer_list = get_offer_list(self.subsession, False)
    
        template_vars = {}
    
        for i in range(5):
            template_vars[f'selleroffer{i + 1}'] = seller_list[i][1]
            template_vars[f'buyeroffer{i + 1}'] = buyer_list[i][1]
        
        return template_vars
    
    def live_method(self, data):
        if 'next' in data:
            for player in self.subsession.get_players():
                player.participant.vars['notready'] = True
                
            self.subsession.session.vars['ready'] = 0
            
            self.subsession.session.vars['adminround'] = self.subsession.session.vars.get('adminround', 1) + 1
            
            if self.round_number == C.NUM_ROUNDS:
                chart.create_charts(self.subsession, C.NUM_ROUNDS)
            
            return {0: {'next': 'next'}}
            
        if 'offer' in data:
            try:
                if int(data['offer']) >= 0:
                    
                    if self.seller:
                        if int(data['offer']) < self.cost:
                            return {self.id_in_group: {'error': "Ihr Angebot muss grösser als ihre kosten sein."}}
                    else:
                        if int(data['offer']) > self.cost:
                            return {self.id_in_group: {'error': "Ihr Angebot muss kleiner als ihre einschätzung sein."}}
                        
                    self.offer = int(data['offer'])
                    
                    if self.seller:
                        seller_list = get_offer_list(self.subsession, True)
                        return {1: {'seller': seller_list}, self.id_in_group: {'offer': "Sie haben das Produkt für " + str(self.offer) + " Punkte angeboten."}}
                    else:
                        buyer_list = get_offer_list(self.subsession, False)  
                        return {1: {'buyer': buyer_list}, self.id_in_group: {'offer': "Sie haben ein Kaufangebot für " + str(self.offer) + " Punkte gemacht."}}
                else:
                    return {self.id_in_group: {'error': 'die Eingabe ist ungültig'}}
            
            except ValueError:
                return {self.id_in_group: {'error': 'die Eingabe ist ungültig'}}
            
        if 'buy' in data:
            if self.seller:
                list = get_offer_list(self.subsession, False)
            else:
                list = get_offer_list(self.subsession, True)
                
            if self.seller:
                if int(list[0][1]) < self.cost:
                    return {self.id_in_group: {'error': "Sie könnnen das Produkt nicht günstiger als ihre Produktionskosten verkaufen."}}
            else:
                if int(list[0][1]) > self.cost:
                    return {self.id_in_group: {'error': "Sie könnnen das Produkt nicht teurer als ihre Schätzung kaufen."}}
                
            players = self.subsession.get_players()
            player = [p for p in players if int(p.id_in_group) == int(list[0][0])][0]
                
            self.deal = int(list[0][1])
            player.deal = int(list[0][1])
            
            self.participant.vars['notready'] = False
            player.participant.vars['notready'] = False
            
            self.subsession.session.vars['ready'] = self.subsession.session.vars.get('ready', 0) + 2
            
            if self.seller:
                self.participant.vars['points'] = self.participant.vars.get('points', 0) + (self.deal - self.cost)
                player.participant.vars['points'] = player.participant.vars.get('points', 0) + (player.cost - player.deal)
            else:
                self.participant.vars['points'] = self.participant.vars.get('points', 0) + (self.cost - self.deal)
                player.participant.vars['points'] = player.participant.vars.get('points', 0) + (player.deal - player.cost)
            
            seller_list = get_offer_list(self.subsession, True)
            buyer_list = get_offer_list(self.subsession, False)
            
            sellerstr = "Sie haben das Produkt für " + str(self.deal) + " Punkte verkauft."
            buyerstr = "Sie haben das Produkt für " + str(self.deal) + " Punkte gekauft."
            
            if self.seller:    
                return {1: {'seller': seller_list, 'buyer': buyer_list, 'readyadmin': self.subsession.session.vars.get('ready', 0)}, self.id_in_group: {'buy': sellerstr, 'points': self.participant.vars.get('points', 0)}, player.id_in_group: {'buy': buyerstr, 'points': player.participant.vars.get('points', 0)}}
            else:
                return {1: {'seller': seller_list, 'buyer': buyer_list, 'readyadmin': self.subsession.session.vars.get('ready', 0)}, self.id_in_group: {'buy': buyerstr, 'points': self.participant.vars.get('points', 0)}, player.id_in_group: {'buy': sellerstr, 'points': player.participant.vars.get('points', 0)}}       
            

class result(Page):
    template_name = '_templates/result.html'

    def is_displayed(self):
        return self.round_number == C.NUM_ROUNDS
    
    def vars_for_template(player):
        return dict(
            urls = [[1, 'PDF/charts/chart.png']]
        )    
        
    def live_method(self, data):        
        if 'next' in data:
            pdf.create_pdf(['_static/PDF/charts/chart.png'], C.GAME_NAME, self.subsession.get_players())
            
            return {1: {'PDF': 'PDF'}}


page_sequence = [checkin, game, result]
