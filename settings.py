from os import environ
import _templates._python.create_qrcode as create_qrcode

create_qrcode

SESSION_CONFIGS = [
    dict(
        name='nashequilibrium',
        display_name='Nash Equilibrium',
        app_sequence=['game_nashequilibrium'],
        num_demo_participants=3,
    ),
    dict(
        name='publicgood',
        display_name='Public Good',
        app_sequence=['game_publicgood'],
        num_demo_participants=3,
    ),
    dict(
        name='doubleauction',
        display_name='Double Auction',
        app_sequence=['game_doubleauction'],
        num_demo_participants=3,
    ),
]

ROOMS = [
    dict(
        name='economication',
        display_name='Economication',
    )
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

LANGUAGE_CODE = 'de'

REAL_WORLD_CURRENCY_CODE = 'CHF'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
AUTH_LEVEL = "STUDY"

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '2099813542602'
