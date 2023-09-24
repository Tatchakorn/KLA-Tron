from src._global import (
    DB_NAME,
    ADDR_LST,
)


from src.DBHandler import TokenBalanceDBHandler

DATA_TXT = '[DATA]:'
FUNC_CALL = '[Calling] --'


class TestDB:
    
    def __init__(self):
        print('[TEST] TestDB')
        self.db_handler = TokenBalanceDBHandler(DB_NAME)

    
    def get_all_from_addr(self):
        print(f'{FUNC_CALL} get_all_from_addr()')
        
        for a in ADDR_LST:
            addr, id_ = a.get('addr'), a.get('id')
            print(f'{DATA_TXT} addr: {addr}, id: {id_}')
            
            ##### Actual test < #####
            
            print(f'>> get_all_token_bal("{addr}")')
            token_bal_lst = self.db_handler.get_all_token_bal(addr)
            token_lst = [t[0] for t in token_bal_lst]
            print('Tether USD' in token_lst)
            
            ##### Actual test > #####


    def run_test(self):
        self.get_all_from_addr()


class MainTest:
    
    def __init__(self):
        print('[BEGIN] testing ...')
        t_db = TestDB()
        t_db.run_test()

if __name__ == '__main__':
    MainTest()