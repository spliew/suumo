# -*- coding: utf-8 -*-
from django.shortcuts import render
from .forms import MyForm
from urllib.request import urlopen
from bs4 import BeautifulSoup
import sys, pickle
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
            h1, ps, predictions = process(url)
            # 結果表示ページに渡すデータ
            context = {
                'url':url,
                'h1': h1,
                'ps':ps,
                'predictions': predictions
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
    text = ""
    for p in ps:
        text = text + ';' + p.get_text()
    ps = text.split(';')

    predictions = predict(text)    
    return h1, ps, predictions


def predict(text):
    """
    textから分析してクラスを予測する
    :param text: Str
    :return predictions: dict(): クラスの行列(予測クラスなら100、でないなら0)
    出力例: 予測クラスが2 なら {'エンタメ':0, 'スポーツ':100,...}
    """

    categories = "エンタメ スポーツ おもしろ 国内 国外 コラム IT科学 グルメ".split() # カテゴリーのリスト

    # with open('1486962747.pickle', 'rb') as pickle_file:
    #     model=pickle.load(pickle_file)
    # x = int(model.predict(text))
    # probs =  [0]*8
    # probs[x] = 100

    predictions = {}
    for i in range(len(categories)):
        predictions[categories[i]] = 1 # probs[i]
  
    return predictions
