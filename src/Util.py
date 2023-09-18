import json

class Util:
    
    @staticmethod
    def write_f_js(txt: str):
        txt = json.dumps(txt, indent=4)
        with open('out.txt', 'w') as f:
            f.write(txt)
    
    @staticmethod
    def append_f_js(txt: str):
        txt = json.dumps(txt, indent=4)
        with open('out.txt', 'a') as f:
            f.write(txt)