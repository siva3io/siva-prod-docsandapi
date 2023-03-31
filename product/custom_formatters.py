import re

from bs4 import BeautifulSoup
from selectorlib import Formatter


class PriceFormatter(Formatter):
    def format(self, text):
        price = re.findall(r'\d+\.\d+', text)
        if price:
            return price[0]
        return 0


class HTMLFormatter(Formatter):
    def format(self, text):
        # function_start = text.find("function")
        # function_end = text[function_start:].rfind(");")
        # # text = text[:function_start] + text[function_end+1:]
        # return text[:function_start]
        data = {}
        soup = BeautifulSoup(text, features="html.parser")
        table = soup.table
        if table is None:
            return soup.get_text()
        for tr in table.findAll('tr'):
            span_tags = tr.findAll('span')
            if len(span_tags) < 2:
                elements = [ele for ele in tr.contents if ele != " "]
                if len(elements) < 2:
                    print("Less than 2 available", elements, tr)
                    continue
                key = elements[0].get_text().strip()
                value = elements[1].get_text().strip()
            else:
                key = span_tags[0].get_text().strip()
                value = span_tags[1].get_text().strip()
            # breakpoint()
            value = value.encode("ascii", "ignore").decode()
            data[key] = value
        return data
