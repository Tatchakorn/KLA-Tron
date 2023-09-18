'''
$ Transfer API ( from addr )
# addr -> balance
'''

from src.Util import Util
from src._global import dbg, ADDR_LST, LOG_ENABLE, DB_NAME
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


class Main:

    def __init__(self):
        dbg('[BEGIN] ----- Main -----')
        self.run()
        dbg('[END]   ----- Main -----')
    
    @staticmethod
    def _run_task():
        message = '------ Balance updated!! ------ \n'
        send_update = False
        addr_lst = ADDR_LST
        
        
        for addr in addr_lst:
            address = addr.get('addr')
            name = addr.get('id')
            
            logger.info(f'Getting address for: {name}')
            
            acc = Account(**addr)
            message += f'Address: {address}\n'
            message += f'Name: {name}\n'
            
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
                if prev_bal != bal:
                    logger.info(f'[COMPARE] {bal}(bal) != {prev_bal}(prev_bal)')
                    n_bal = float(bal.replace(',', ''))
                    n_prev_bal = float(prev_bal.replace(',', ''))
                    change_str = ''
                    
                    if n_bal > n_prev_bal:
                        change_str = f'({urllib.parse.quote_plus("+")}) {"{:,.2f}".format(n_bal - n_prev_bal)}'
                    else:
                        change_str = f'(-) {"{:,.2f}".format(n_prev_bal - n_bal)}'
                    
                    message += f'[{token}] -> balance: {bal} (New!) \n'
                    message += f'<change: {change_str}>\n'
                    insert_res = db_handler.update_balance(address, token, bal)
                    logger.info(f'[UPDATE] ({address}, {token}, {bal}) : {insert_res}')
                    
                    send_update = True
                else:
                    message += f'[{token}] -> balance: {bal}\n'
                logger.info(f'token: {token}, balance: {bal}')
            
            message += f'{"-"*40}\n'
        
        logger.info(f'send_update: {send_update}')
        logger.info(message)
        
        n = Notification()
        chat_ids = ['6505704846', '1437421739', '6143460504', '6192414506']
        
        if send_update:
            n.get_updates()
            for c in chat_ids:
                n.send_message(c, message)
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