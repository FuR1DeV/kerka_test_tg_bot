import os
from pyqiwip2p import QiwiP2P
from dotenv import load_dotenv
from emoji import emojize

load_dotenv()

HOST = os.getenv('HOST')
POSTGRESQL_USER = os.getenv('POSTGRESQL_USER')
POSTGRESQL_PASSWORD = os.getenv('POSTGRESQL_PASSWORD')
DATABASE = os.getenv('DATABASE')

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))
P2P = QiwiP2P(auth_key=os.getenv('QIWI_PRIVATE_KEY'))

DOWN = emojize('🔽🔽🔽🔽🔽🔽🔽🔽')
HELLO = emojize(':man_raising_hand:')
ROBOT = emojize(':robot:')
COOL = emojize(':smiling_face_with_sunglasses:')
USER = emojize(':user:')
ID = emojize(':ID_button:')
NAME = emojize(':bust_in_silhouette:')
MONEY = emojize(':dollar_banknote:')
BAN = emojize(':no_entry:')
NOT_BAN = emojize(':check_mark_button:')
