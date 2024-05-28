from bs4 import BeautifulSoup
import requests
import stockdata
import os
import pandas as pd

savefile = "./stockinfo/semiconductor_corr.csv"

if not os.path.exists(savefile):
    text = requests.get("https://finance.naver.com/sise/sise_group_detail.naver?type=theme&no=307").text
    soup = BeautifulSoup(text, "html.parser")
    result = {}
    stocks = soup.find_all("td", {"class":"name"})
    for stock in stocks:
        code = (stock.find('a').get('href')).replace('/item/main.naver?code=', '')
        name = stock.get_text().split(' *')[0]
        if "*" in stock.get_text():
            code += ".KQ"
        else:
            code += ".KS"
        result[code] = name

    dataset = stockdata.create_dataset(result.keys(), stockdata.today_before(50), stockdata.today(), '5m')
    dataset = stockdata.normalize(dataset)
    dataset.corr().to_csv(savefile)

corr_matrix = pd.read_csv(savefile, index_col=0)
# 상관관계가 0.8 이상인 모든 쌍 찾기
threshold = 0.9
high_corr_pairs = []

# 상삼각 행렬만 검사하여 중복을 피함
for i in range(len(corr_matrix.columns)):
    for j in range(i + 1, len(corr_matrix.columns)):
        if corr_matrix.iloc[i, j] >= threshold:
            high_corr_pairs.append((corr_matrix.index[i], corr_matrix.columns[j], corr_matrix.iloc[i, j]))

# 결과 출력
for pair in high_corr_pairs:
    print(f"{pair[0]}와 {pair[1]}의 상관관계: {pair[2]}")