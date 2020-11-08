from flask import Flask, request, abort
import os
from googletrans import Translator 

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

app = Flask(__name__)
translator = Translator()

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/")
def hello_world():
    return "hello world!"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


def reply_example_context(word):
    # twitterから英単語の使用例をピックアップ
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

    CK = 'PeiYuO3tpGyuufkhrmYTk64DL' # コンシューマーキー
    CKS = 'fNCxf1l4czFfRfwTSaflPXHPn77VnvqfQFuvEJoiYUTq8ohCKx' # コンシューマーシークレット
    AT = '1545825608-PSzllmzEUVMbSGBJHeerMxGKx3w6YeI2j6MsRSw' # アクセストークン
    ATS = 'ojDrCFhSwiB4EqDSG8p4PY5OPZNHapmoUH9jQH5h0LMfa' # アクセストークンシークレット
    count = 1
    n = 1
    print("=====call search_tweets")
    tweets = search_tweets(CK, CKS, AT, ATS, word, count, n)
    example_context = tweets[0]["text"]
    return example_context
    # line_bot_api.reply_message(
    #     event_token,
    #     TextSendMessage(text=example_context))
    # # 画像がある場合は画像もリプライ
    # if len(tweets[0]["image"]) > 0:
    #     line_bot_api.reply_message(
    #         event_token,
    #         ImageSendMessage(original_content_url=tweets[0]["image"][0], preview_image_url=tweets[0]["image"][0]))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # ユーザから送られてきたメッセージ
    user_text = event.message.text
    translated = translator.translate(user_text, dest="ja")
    translated_text = translated.text
    example_context = reply_example_context(user_text)
    print(translated_text, example_context)
    line_bot_api.reply_message(
        event.reply_token,
        [TextSendMessage(text=translated_text),
        TextSendMessage(text=example_context)])

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)

"""
git init
git add requirements.txt translate_bot.py runtime.txt Procfile
git commit -m "first commit"
git push heroku master
# herokuのリモートリポジトリを作成
heroku git:remote -a translater-bot-202011
git push heroku master

# line_botのwebhoolの設定
https://translater-bot-202011.herokuapp.com/callback

# herokuのエラ-ログ確認
heroku logs --tail 
"""
