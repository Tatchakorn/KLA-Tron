import requests
from sys import _getframe as get_f
import os


################################################
BASE_URL = 'https://apilist.tronscanapi.com/api/'
LOG_PATH = './logs/app.log'
DEBUG_ENABLE = False
LOG_ENABLE = False

HEADERS = {
    'Accept': 'application/json',
    #'Authorization': f'ApiKey {self.passwd}'
    }
    
TELEGRAM_API_BASE_URL = 'https://api.telegram.org/bot'
BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'{TELEGRAM_API_BASE_URL}{BOT_TOKEN}'
DB_NAME = 'TokenBalance.db'
CHAT_IDS = ['6505704846', '1437421739', '6143460504', '6192414506']


def tron_addr_url(addr: str) -> str:
    return f'https://tronscan.org/#/address/{addr}'


ADDR_LST = [
    {
       'addr': 'TBLjcanTSDuAPxP59uFFQUJsEvYPn91ic1', 
       'id': 'Few'
    },
    {
        'addr': 'TBrUnjrTynzQSHSnPg7xsK2dDtdALBp94r', 
        'id': 'Tawan 1'
    },
    {
        'addr': 'TEMc7yUEaqJYxhuZby2H4a4mdZD3y7f8KR', 
        'id': 'Tawan 2'
    },
    {
        'addr': 'TU1UuY7zxVtxJe1wSGK1eXhPgiTGzANu6N', 
        'id': 'Tawan 3'
    },
    {
        'addr': 'TAKmFcyPKtivgKz7JmXVDaih2T1s3hHrBK', 
        'id': 'Tawan 4'
    },
    {
        'addr': 'TKQgV95wcsrPKQXL2qssT1ng6aaojwed7w', 
        'id': 'Fourwheel'
    },
]
################################################


def dbg(*arg):
    if DEBUG_ENABLE:
        print(*arg)
