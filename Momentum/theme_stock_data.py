import requests
from bs4 import BeautifulSoup

def semiconductor():
    text = requests.get("https://finance.naver.com/sise/sise_group_detail.naver?type=theme&no=307").text
    soup = BeautifulSoup(text, "html.parser")
    codes = list()
    stocks = soup.find_all("td", {"class":"name"})
    for stock in stocks:
        code = (stock.find('a').get('href')).replace('/item/main.naver?code=', '')
        name = stock.get_text().split(' *')[0]
        if "*" in stock.get_text():
            code += ".KQ"
        else:
            code += ".KS"
        codes.append(code)
    return codes