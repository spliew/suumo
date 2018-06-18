# -*- coding: utf-8 -*-
from django.shortcuts import render
from .forms import MyForm
from urllib.request import urlopen
from bs4 import BeautifulSoup
import sys, pickle, re
import pandas as pd
import lightgbm as lgb
from sklearn import preprocessing

# from MultivariateBernoulli import *


def top(request):
    """top ページを返す"""
    return render(request, "top.html")

def result(request):
    """結果ページを返す"""
    if request.method == "POST":
        form = MyForm(data=request.POST)
        if form.is_valid():
            url = request.POST['url']
            h1, ps, predictions, h9 = process(url)
            # 結果表示ページに渡すデータ
            context = {
                'url':url,
                'h1': h1,
                'ps':ps,
                'predictions': predictions,
                'h9': str(h9)
            }
            return render(request, "result.html", context)
    else:
        return render(request, "top.html")

def process(url):
    """
    urlからのデータをscrapeして結果を返す
    :param url: Str
    :return h1: Str: タイトル
    :return ps: list of Str: コンテンツ
    :return predictions: dict(): クラスの行列(予測クラスなら100、でないなら0)
    出力例: 予測クラスが2 なら {'エンタメ':0, 'スポーツ':100,...}
    """
    soup = BeautifulSoup(urlopen(url).read())
    h1 = soup.find("h1").get_text()
    ps = soup.find_all("p")
    body = soup.find("body")
    head = soup.find("head")

    tezt =  str(head.find_all("script",{'type':'text/javascript'})[-2])
    test = tezt.split('{')[1].split('}')[0].replace('\n\t','').replace('\n','')
    text = ""
    for p in ps:
        text = text + ';' + p.get_text()
    ps = text.split(';')

    kai = body.find_all('td',text=re.compile('階'))[0].text
    kai1 = kai.split('/')[0][0]
    height = kai.split('/')[1][0]

    for i in test.split(','):
        if 'shikugunNm' in i:
            pig = re.findall('"([^"]*)"', i)[0]
            if '川崎市' in pig:
                pig = pig.split('川崎市')[1]
        if 'madoriDisp' in i:
            madori = re.findall('"([^"]*)"', i)[0]
        if 'chikugonensu' in i:
            chiku = re.findall('"([^"]*)"', i)[0]
        if 'mensekiDisp' in i:
            menseki = re.findall('"([^"]*)"', i)[0]
        if 'ensenNm1' in i:
            sen1 = re.findall('"([^"]*)"', i)[0]
        if 'ekiNm1' in i:
            eki1 = re.findall('"([^"]*)"', i)[0]
        if 'ensenNm2' in i:
            sen2 = re.findall('"([^"]*)"', i)[0]
        if 'ekiNm2' in i:
            eki2 = re.findall('"([^"]*)"', i)[0]
        if 'ensenNm3' in i:
            sen3 = re.findall('"([^"]*)"', i)[0]
        if 'ekiNm3' in i:
            eki3 = re.findall('"([^"]*)"', i)[0]
        if 'tohoJikan1' in i:
            toho1 = re.findall('"([^"]*)"', i)[0]
        if 'tohoJikan2' in i:
            toho2 = re.findall('"([^"]*)"', i)[0]
        if 'tohoJikan3' in i:
            toho3 = re.findall('"([^"]*)"', i)[0]
        if 'busJikan1' in i:
            bus1 = re.findall('"([^"]*)"', i)[0]
        if 'busJikan2' in i:
            bus2 = re.findall('"([^"]*)"', i)[0]
        if 'busJikan3' in i:
            bus3 = re.findall('"([^"]*)"', i)[0]
        if 'chinryo' in i:
            chin = re.findall('"([^"]*)"', i)[0]
        if 'kanrihi' in i:
            kanri = re.findall('"([^"]*)"', i)[0]

    h9 = int(chin) + int(kanri)
    dk = 0
    k = 0
    l = 0
    s = 0
    

    if 'DK' in madori:
        dk =1
        madori.replace('DK','')
    if 'K' in madori:
        k = 1
    if 'l' in madori:
        l = 1
    if 's' in madori:
        s = 1

    ans = [pig,dk,k,l,s,chiku,height,kai1,menseki,sen1,eki1+'駅',toho1,sen2,eki2+'駅',toho2,sen3,eki3+'駅',toho3,bus1,bus2,bus3]

    dfn = pd.DataFrame([ans],columns=['区', '間取りDK', '間取りK', '間取りL', '間取りS', '築年数', '建物高さ', '階1', '専有面積', \
       '路線1', '駅1', '徒歩1', '路線2', '駅2', '徒歩2', '路線3', '駅3', '徒歩3', 'バス1', \
       'バス2', 'バス3'])

    dfn[['築年数', '建物高さ', '階1', '専有面積',
       '徒歩1', '徒歩2', '徒歩3','バス1','バス2','バス3']] = dfn[['築年数', '建物高さ', '階1', '専有面積', \
       '徒歩1', '徒歩2', '徒歩3','バス1','バス2','バス3']].apply(pd.to_numeric)

    categorial_features = ['区', '間取りDK', '間取りK', '間取りL', '間取りS', \
       '路線1', '駅1', '路線2', '駅2', '路線3', '駅3']

    
    with open('encoder3.p','rb') as hand:
        lbl = pickle.load(hand)

    with open('model3.p','rb') as hand:
        lgb_clf = pickle.load(hand)

    for col in categorial_features:
        dfn[col] = lbl.fit_transform(dfn[col].astype(str))

    predictions = int(lgb_clf.predict(dfn))


    return h1, ps, predictions, h9


# def predict(text):
#     """
#     textから分析してクラスを予測する
#     :param text: Str
#     :return predictions: dict(): クラスの行列(予測クラスなら100、でないなら0)
#     出力例: 予測クラスが2 なら {'エンタメ':0, 'スポーツ':100,...}
#     """

#     # categories = "エンタメ スポーツ おもしろ 国内 国外 コラム IT科学 グルメ".split() # カテゴリーのリスト

#     # with open('1486962747.pickle', 'rb') as pickle_file:
#     #     model=pickle.load(pickle_file)
#     # x = int(model.predict(text))
#     # probs =  [0]*8
#     # probs[x] = 100

#     predictions = {}
#     for i in range(len(categories)):
#         predictions[categories[i]] = 1 # probs[i]
  
#     return predictions

