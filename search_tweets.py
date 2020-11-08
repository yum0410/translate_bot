import requests
from requests_oauthlib import OAuth1
import urllib
from tqdm import tqdm


def search_tweets(CK, CKS, AT, ATS, word, count, n):
    # 文字列設定
    word += ' exclude:retweets' # RTは除く
    word = urllib.parse.quote_plus(word)
    # リクエスト
    url = "https://api.twitter.com/1.1/search/tweets.json?lang=ja&q="+word+"&count="+str(count)
    auth = OAuth1(CK, CKS, AT, ATS)
    response = requests.get(url, auth=auth)
    data = response.json()['statuses']

    cnt = 0
    tweets = []
    bar = tqdm(total = n)

    while True:
        bar.update(1)
        if len(data) == 0:
            break
        cnt += 1
        if cnt > n:
            break
        for tweet in data:
            maxid = int(tweet["id"]) - 1

            images = [m["media_url"] for m in tweet["extended_entities"]["media"]] if tweet.get("extended_entities") else []
            _tweet = {
                "id": tweet["id"],
                "created_at": tweet["created_at"],
                "user": tweet["user"]["name"],
                "user_description": tweet["user"]["description"],
                "text": tweet["text"],
                "retweet_count": tweet["retweet_count"],
                "image": images
                }         
            tweets.append(_tweet)
        # 2回目以降のリクエスト
        url = "https://api.twitter.com/1.1/search/tweets.json?lang=ja&q="+word+"&count="+str(count)+"&max_id="+str(maxid)
        response = requests.get(url, auth=auth)
        try:
            data = response.json()['statuses']
        except KeyError: # リクエスト回数が上限に達した場合のデータのエラー処理
            print('上限まで検索しました')
            break
    return tweets