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
    FORCE_SEND, 
    CHAT_IDS, 
    tron_addr_url,
)
from src.TronScan import Account
from src.Notification import Notification
from src.DBHandler import TokenBalanceDBHandler
import logging
import schedule
import time
import urllib.parse

logging.basicConfig(
    filename='noti.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
logger.disable = not LOG_ENABLE
db_handler = TokenBalanceDBHandler(DB_NAME)

class MessageHandler:
    
    def __init__(self):
        self.msg = '---------- Balance Updated ----------\n'
    
    
    def append(self, *msg):
        for m in msg:
            self.msg += f'{m}\n'

    def append_line(self):
        self.msg += f'{"-" * 50}\n'
    
    def get(self):
        return self.msg
    
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
            
            for d in acc.get_bal_lst():
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
                
                # print('bal:',type(bal), bal)
                # print('prev_bal:',type(prev_bal), prev_bal)
                # print('prev_bal == bal?:', prev_bal == bal)
                
                n_bal = float(bal.replace(',', ''))
                n_prev_bal = float(prev_bal.replace(',', ''))
                
                if prev_bal != bal and abs(n_bal - n_prev_bal) > 1000:
                    send_update = True # ====> Send updated balance !!!
                    logger.info(f'[COMPARE] {bal}(bal) != {prev_bal}(prev_bal)')
                    logger.info(f'[COMPARE] abs(n_bal - n_prev_bal) < 1000 {abs(n_bal - n_prev_bal) < 1000}')

                    change_str = ''
                    

                    if n_bal > n_prev_bal:
                        # change_str = f'({urllib.parse.quote_plus("+")}) {"{:,.2f}".format(n_bal - n_prev_bal)}'
                        change_str = f'(➕) {"{:,.2f}".format(n_bal - n_prev_bal)}'
                    else:
                        change_str = f'(➖) {"{:,.2f}".format(n_prev_bal - n_bal)}'
                    
                    if token == 'Tether USD':
                        token = 'USD'
                    
                    msg.append(
                        f'[{token}] balance: 💲**{bal}** (New!)',
                        f'<{change_str}>',
                        )
                    insert_res = db_handler.update_balance(address, token, bal)
                    logger.info(f'[UPDATE] ({address}, {token}, {bal}) : {insert_res}')
                    
                else:
                    msg.append(f'[{token}] -> balance: 💲**{bal}**')
                
                logger.info(f'token: {token}, balance: {bal}')
            
            msg.append_line()
        
        logger.info(f'=====> send_update: {send_update}')
        logger.info(msg.get())
        
        n = Notification()
        chat_ids = CHAT_IDS

        if send_update or FORCE_SEND:
            # n.get_updates()
            for c in chat_ids:
                n.send_message(c, msg.get())
        send_update = False
    
    
    def run(self):
       schedule.every(1).minutes.do(self._run_task)
       # schedule.every(1).seconds.do(self._run_task)
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
       
       finally:
          logger.info('----- [Closing DB connection] -----')
          db_handler.close_connection()


if __name__ == '__main__':
    Main()