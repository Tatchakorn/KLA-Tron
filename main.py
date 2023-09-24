'''
$ Transfer API ( from addr )
# addr -> balance
'''

from src.Util import Util
from src._global import (
    dbg, 
    ADDR_LST, 
    LOG_ENABLE, 
    DB_NAME, 
    CHAT_IDS, 
    tron_addr_url,
    LOG_PATH,
)
from src.TronScan import Account
from src.Notification import Notification
from src.DBHandler import TokenBalanceDBHandler
import logging
import schedule
import time
import urllib.parse
import os

########################################
# GLOBAL SETUP
logging.basicConfig(
    filename=LOG_PATH, 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
logger.disable = not LOG_ENABLE
db_handler = TokenBalanceDBHandler(DB_NAME)
########################################


class MessageHandler:
    
    def __init__(self):
        self.msg = '----- Balance Updated (V3) -----\n'
    
    def append(self, *msg):
        for m in msg:
            self.msg += f'{m}\n'

    def append_line(self):
        self.msg += f'{"-" * 20}\n'
    
    def get(self):
        return self.msg
    
    @staticmethod
    def format_token(token):
        return token if token != 'Tether USD' else 'USD'
    
    @staticmethod
    def to_hypertext_tron(txt):
        '''
        [Click here](https://example.com) 
        <a href=""></a>
        '''
        return f'[{txt}]({tron_addr_url(txt)})'


class Main:

    def __init__(self):
        dbg('[BEGIN] ----- Main -----')
        self.run()
        dbg('[END]   ----- Main -----')


    @staticmethod
    def _clean_log():
        try:
            with open(LOG_PATH, 'w') as f:
                now = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                f.write(f'{now} => [LOG CLEARED]')
        except Exception as e:
            print(f'_clean_log: {e}')

    
    @staticmethod
    def _run_task():
        
        send_update = False
        addr_lst = ADDR_LST
        msg = MessageHandler()
        
        for addr in addr_lst:
            address = addr.get('addr')
            name = addr.get('id')
            
            logger.info(f'Getting address for: {name}')
            
            acc = Account(**addr)
            
            msg.append(
                msg.to_hypertext_tron(address), 
                name)
            
            # get balance from Tron API
            curr_balance_lst = acc.get_bal_lst()
            curr_token_lst = [d.get('token') for d in balance_lst]
            
            # get all tokens for this addr from DB
            prev_token_bal_lst = self.db_handler.get_all_token_bal(address)
            prev_token_lst = [t[0] for t in prev_token_bal_lst]
            common_token_set = set(prev_token_lst).intersection(set(curr_token_lst))
            set_zero_lst = list(set(prev_token_lst) - common_token_set)
            
            for token in set_zero_lst:
                curr_balance_lst.append({'token': 'token', 'balance': '0'})

            
            for d in curr_balance_lst:
                token = d.get('token')
                bal = d.get('balance')
                
                prev_bal = db_handler.get_balance(address,token)
                logger.info(f'prev_bal (token: {token}, address: {address}): {prev_bal}')
                logger.info(f'Balance from DB: {db_handler.get_balance(address,token)}')

                if prev_bal is None:
                    insert_res = db_handler.insert_balance(address, token, bal)
                    
                    logger.info('----- prev_bal is None -----')
                    logger.info(f'[INSERT] ({address}, {token}, {bal}) : {insert_res}')
                    prev_bal = db_handler.get_balance(address,token)
                    logger.info(f'[After Insert]Balance from DB: {db_handler.get_balance(address,token)}')
                
                n_bal = float(bal.replace(',', ''))
                n_prev_bal = float(prev_bal.replace(',', ''))
                
                if prev_bal != bal: # Update whenever there is a difference
                    insert_res = db_handler.update_balance(address, token, bal)
                    logger.info(f'[UPDATE] ({address}, {token}, {bal}) : {insert_res}')
                
                if prev_bal != bal and abs(n_bal - n_prev_bal) > 1000:
                    send_update = True # ====> Send updated balance !!!
                    logger.info(f'[COMPARE] {bal}(bal) != {prev_bal}(prev_bal)')
                    logger.info(f'[COMPARE] abs(n_bal - n_prev_bal) < 1000 {abs(n_bal - n_prev_bal) < 1000}')

                    change_str = ''
                    

                    if n_bal > n_prev_bal:
                        change_str = f'(➕) {"{:,.2f}".format(n_bal - n_prev_bal)}'
                    else:
                        change_str = f'(➖) {"{:,.2f}".format(n_prev_bal - n_bal)}'
                    
                    
                    msg.append(
                        f'[{msg.format_token(token)}] Balance: 💲**{bal}** (New!)',
                        f'<{change_str}>',
                        )
                    
                else:
                    msg.append(f'[{msg.format_token(token)}] balance: 💲**{bal}**')
                
                logger.info(f'token: {token}, balance: {bal}')
            
            msg.append_line()
        
        logger.info(f'=====> send_update: {send_update}')
        logger.info(msg.get())
        
        n = Notification()
        chat_ids = CHAT_IDS
        
        ##############################
        ##### TEST SEND
        # FORCE_SEND = True
        ##############################
        
        
        if send_update or FORCE_SEND:
            n.get_updates()
            for c in chat_ids:
                n.send_message(c, msg.get())
        send_update = False
    
    
    def run(self):
       schedule.every(1).minutes.do(self._run_task)
       schedule.every().day.at('00:00').do(self._clean_log)
       logger.info('Starting ...')
       ##############################
       ##### TEST SEND
       # self._run_task()
       # db_handler.close_connection()
       # exit()
       ##############################
       try:
          while True:
            schedule.run_pending()
            time.sleep(1)
       except Exception as e:
          logger.error(f'{str(e)}')
          logger.error(f'=====> Restarting...')
          time.sleep(1)
          schedule.clear()
          time.sleep(1)
          self.run()
       
       finally:
          logger.info('----- [Closing DB connection & logger] -----')
          db_handler.close_connection()
          logger.shutdown()


if __name__ == '__main__':
    Main()