from src._global import dbg, get_f, TELEGRAM_API_BASE_URL, BOT_TOKEN, TELEGRAM_API_URL
from src.Util import Util
import requests


def action_url(action: str):
    return f'{TELEGRAM_API_URL}/{action}'


class Notification:
    
    def __init__(self):
        dbg('[INIT: Notification]')
    
    def get_updates(self):
        dbg(f'(call) -> {get_f().f_code.co_name}')
        url = action_url('getUpdates')
        dbg(f'[VAR: url] <{url}>')
        response = requests.get(url).json()
        Util.write_f_js(response)
     
     
    def send_message(self, chat_id: str, txt: str):
        dbg(f'(call) -> {get_f().f_code.co_name}')
        url = f'{action_url("sendMessage")}?chat_id={chat_id}&text={txt}'
        requests.post(url)
        dbg(f'[VAR: url] <{url}>')