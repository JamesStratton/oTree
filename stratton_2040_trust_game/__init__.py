from otree.api import *



doc = """
James Stratton's ECON2040 Trust Game
"""

class Constants(BaseConstants):
    name_in_url = 'stratton_2040_trust_game'
    players_per_group = 2
    num_rounds = 3
    endowment = cu(10)
    instructions_template = 'stratton_2040_trust_game/instructions.html'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    sent_amount = models.CurrencyField(
        min=cu(0),
        max=Constants.endowment,
        doc="""Amount sent by Player A""",
        label="How much do you want to send to Player B?",
    )
    message = models.LongStringField(
        blank=True,
        label="If you'd like to, you can leave a message for Player B. (This is optional.)"
    )
    sent_back_amount = models.CurrencyField(
        doc="""Amount sent back by Player B""",
        label="How much do you want to send back?",
    )
    multiplication_factor = models.IntegerField()
    round_incentivized = models.IntegerField()

def creating_session(subsession):
    import random
    for group in subsession.get_groups():
        group.multiplication_factor = random.choice([3,6])
        group.round_incentivized = random.choice([1,2,3])

class Player(BasePlayer):
    pass


# FUNCTIONS
def sent_back_amount_choices(group: Group):
    return currency_range(cu(0), group.sent_amount * group.multiplication_factor, cu(1))


def set_payoffs(group: Group):
    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)
    p1.payoff = Constants.endowment - group.sent_amount + group.sent_back_amount
    p2.payoff = group.sent_amount * group.multiplication_factor - group.sent_back_amount

# PAGES
class Send(Page):
    form_model = 'group'
    form_fields = ['sent_amount', 'message']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1


class WaitForP1(WaitPage):
    pass


class SendBack(Page):
    form_model = 'group'
    form_fields = ['sent_back_amount']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        return dict(tripled_amount=group.sent_amount * group.multiplication_factor)


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

class Results(Page):
    pass

class FinalResultsWaitPage(WaitPage):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 3

class PaymentPage(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 3

page_sequence = [Send, WaitForP1, SendBack, ResultsWaitPage, Results, FinalResultsWaitPage, PaymentPage]