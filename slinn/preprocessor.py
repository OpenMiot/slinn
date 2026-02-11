import re
import urllib.parse
import html
from . import utils


class Preprocessor:

    """
    Pages preprocessor
    """
    
    @staticmethod
    def get_nested_value(obj, key_path):
        current = obj
        parts = key_path.split('.')
        for part in parts:
            if isinstance(current, dict):
                if part in current:
                    current = current[part]
                else:
                    return None
            else:
                try:
                    current = getattr(current, part)
                except AttributeError:
                    return None
        return current
    
    def __init__(self, open_quote: str = '<%', close_quote: str = '%>') -> None:
        self.open_quote = open_quote
        self.close_quote = close_quote
        self.pattern = lambda element='.*': fr'{self.open_quote}\s*{element}\s*{self.close_quote}'
        
    def replace_conditions(self, text: str, data: dict) -> str:
        for precondition in re.findall(fr'{self.open_quote}\s*if\s*[\w\.]+\s*{self.close_quote}[\s\S]+?{self.open_quote}\s*endif\s*{self.close_quote}', text):
            condition = precondition.replace(re.search(fr'{self.open_quote}\s*endif\s*{self.close_quote}', precondition).group(0), '', 1)
            header = re.search(fr'{self.open_quote}\s*if\s*[\w\.]+\s*{self.close_quote}', condition).group(0)
            cond = header.replace(re.search(fr'{self.open_quote}\s*if\s*', header).group(0), '', 1).replace(re.search(fr'\s*{self.close_quote}', header).group(0), '', 1)
            if not self.get_nested_value(data, cond):
                #print(data, cond, self.get_nested_value(data, cond))
                text = text.replace(precondition, '', 1)
            else:
                text = text.replace(precondition, condition.replace(header, '', 1), 1)
        return text

    def replace(self, text: str, data: dict) -> str:
        for zaloop in re.findall(fr'{self.open_quote}\s*for\s*\w+\s*in\s*\w+\s*{self.close_quote}[\s\S]+?{self.open_quote}\s*end\s*{self.close_quote}', text):
            loop = zaloop.replace(re.search(fr'{self.open_quote}\s*end\s*{self.close_quote}', zaloop).group(0), '', 1)
            header = re.search(fr'{self.open_quote}\s*for\s*\w+\s*in\s*\w+\s*{self.close_quote}', loop).group(0)
            iterator = header.replace(re.search(fr'{self.open_quote}\s*for\s*', header).group(0), '', 1)\
                             .replace(re.search(fr'\s*in\s*\w+\s*{self.close_quote}', header).group(0), '', 1)
            iterable = header.replace(re.search(fr'{self.open_quote}\s*for\s*\w+\s*in\s*', header).group(0), '', 1)\
                             .replace(re.search(fr'\s*{self.close_quote}', header).group(0), '', 1)
            loop = loop.replace(header, '', 1)
            looped = ""
            for it in data[iterable]:
                ll = loop
                ll = self.replace_conditions(ll, {iterator: it})
                while zai := re.search(fr'{self.open_quote}\s*{iterator}[\.\w]+?\s*{self.close_quote}', ll):
                    zai = zai.group(0)
                    i = zai.replace('<%', '', 1).replace('%>', '', 1).strip().removeprefix(iterator+'.')
                    lolkek = self.get_nested_value(it, i)
                    ll = ll.replace(zai, utils.representate(lolkek if lolkek else it).decode(), 1)
                looped += ll
            text = text.replace(zaloop, looped)
        text = self.replace_conditions(text, data)
        for imp in re.findall(fr'{self.open_quote}\s*import\s+.+\s*{self.close_quote}', text):
            filename = imp.removeprefix('<%').removesuffix('%>').strip().removeprefix('import').strip()
            with open(filename, 'r') as f:
                text = text.replace(imp, self.replace(f.read(), data))
        for key in data:
            text = re.sub(self.pattern(r'htmlsafe\s+' + key), html.escape(utils.representate(data[key]).decode()).replace('\\', '\\\\'), text)
        for key in data:
            text = re.sub(self.pattern(r'urlsafe\s+' + key), urllib.parse.quote_plus(utils.representate(data[key]).decode()).replace('\\', '\\\\'), text)
        for key in data:
            text = re.sub(self.pattern(key), utils.representate(self.get_nested_value(data, key)).decode().replace('\\', '\\\\'), text)
        return text

    def preprocess(self, text: str, data: dict) -> str:
        return self.clean(self.replace(text, data))

    def clean(self, text: str) -> str:
        return re.sub(self.pattern(), '', text)

    def count(self, text: str) -> int:
        return len(re.match(self.pattern(), text))

    def count_trash(self, text: str, data: dict) -> int:
        i = self.count(text)
        for i, dat in enumerate(data):
            i_dat = list(dat)[0]
            if text != re.sub(self.pattern(), dat[i_dat], text):
                i -= 1
        return i
