from src._global import dbg
from src.Util import Util
from src._global import BASE_URL, HEADERS, dbg, get_f

from requests.auth import HTTPBasicAuth
import requests
from typing import List
import secret


def format_balance(bal_txt: str):
    '''
    1.) 2 deciaml points
    2.) comma sesparaed balance
    e.g., balance: 100,000.12
    '''
    try:
        formatted_str = '{:,.2f}'.format(float(bal_txt))
        return formatted_str
    except ValueError:
        return "Invalid input"




class Account:
    
    def __init__(self, addr: str, id: str):
        dbg(f'[INIT: Account] \n<addr:{addr}>\n<id:{id}>\n{"-"*10}')
        
        url = f'{BASE_URL}accountv2?address={addr}'
        auth = HTTPBasicAuth('apikey', secret.API_KEY)
        
        dbg(f'[VAR: url] <{url}>')
        dbg(f'[VAR: API_KEY] <{secret.API_KEY}>',)
        
        # Should use try/catch here but too lazy...
        res = requests.get(url, headers=HEADERS, auth=None)
        self.data = res.json()
        # Util.write_f_js(self.data)
        dbg(f'[END: Account]')
    
    
    @staticmethod
    def _parse_bal(token_data: dict) -> [str, str]:
        '''returns token name, balance'''
        dbg(f'(call) -> {get_f().f_code.co_name}')
        
        token_name = token_data.get("tokenName")
        token_decimal = token_data.get("tokenDecimal")
        balance = token_data.get("balance")
        
        dbg(f'[VAR: token_name] <{token_name}>')
        dbg(f'[VAR: token_decimal] <{token_decimal}>')
        dbg(f'[VAR: balance] <{balance}>')
        
        balance = f'{balance[:-token_decimal]}.{balance[-token_decimal:]}'
        dbg(f'[VAR: balance][2] <{balance}>')

        return token_name, balance
    
    def get_bal_lst(self) -> List[dict]:
        '''returns list of token {name, balance}'''
        dbg(f'(call) -> {get_f().f_code.co_name}')
        with_price_tokens = self.data.get('withPriceTokens')
        
        # assert with_price_tokens is not None, 'No data returned !'
        if with_price_tokens is None:
            return []
        dbg(f'[VAR: with_price_tokens] <{with_price_tokens}>')
        
        bal_lst = []
        for token in with_price_tokens:
            token_name, balance = self._parse_bal(token)
            if token_name in ('trx'):
                continue
            bal_lst.append({'token': token_name, 'balance': format_balance(balance)})
        
        return bal_lst
