from src._global import dbg
import sqlite3
'''
# Insert balance
db_handler.insert_balance('0x123456', 'ETH', 100.0)

# Update balance
db_handler.update_balance('0x123456', 'ETH', 150.0)

# Get balance
balance = db_handler.get_balance('0x123456', 'ETH')
print(f'Balance: {balance}')
'''


class TokenBalanceDBHandler:
    def __init__(self, db_name):
        dbg('[INIT: TokenBalanceDBHandler]')
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        # Create the table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS token_balance (
                address TEXT,
                token TEXT,
                balance TEXT
            )
        ''')
        self.conn.commit()

    def insert_balance(self, address, token, balance):
        try:
            self.cursor.execute('''
                INSERT INTO token_balance (address, token, balance)
                VALUES (?, ?, ?)
            ''', (address, token, balance))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            self.conn.rollback()  # Rollback if the address is not unique
            return False

    def update_balance(self, address, token, new_balance):
        try:
            self.cursor.execute('''
                UPDATE token_balance
                SET balance = ?
                WHERE address = ? AND token = ?
            ''', (new_balance, address, token))
            self.conn.commit()
            return True
        except sqlite3.Error:
            self.conn.rollback()
            return False

    def get_balance(self, address, token):
        self.cursor.execute('''
            SELECT balance FROM token_balance
            WHERE address = ? AND token = ?
        ''', (address, token))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    
    def get_all_token_bal(self, address):
        '''returns list of (token, balance)'''
        
        self.cursor.execute('''
            SELECT * FROM token_balance
            WHERE address = ?
        ''', (address,))
        
        result = self.cursor.fetchall()
        if result is not None:
            result = [(r[1], r[2]) for r in result]
        else:
            result = None
        return result


    def close_connection(self):
        self.conn.close()
