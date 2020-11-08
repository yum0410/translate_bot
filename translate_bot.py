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

from search_tweets import search_tweets

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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # ユーザから送られてきたメッセージ
    user_text = event.message.text
    translated = translator.translate(user_text, dest="ja")
    translated_text = translated.text
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=translated_text))
    # reply_example_context(event.reply_token, user_text)

def reply_example_context(event_token, word):
    # twitterから英単語の使用例をピックアップ
    CK = 'PeiYuO3tpGyuufkhrmYTk64DL' # コンシューマーキー
    CKS = 'fNCxf1l4czFfRfwTSaflPXHPn77VnvqfQFuvEJoiYUTq8ohCKx' # コンシューマーシークレット
    AT = '1545825608-PSzllmzEUVMbSGBJHeerMxGKx3w6YeI2j6MsRSw' # アクセストークン
    ATS = 'ojDrCFhSwiB4EqDSG8p4PY5OPZNHapmoUH9jQH5h0LMfa' # アクセストークンシークレット
    count = 1
    n = 1
    tweets = search_tweets(CK, CKS, AT, ATS, word, count, n)
    example_context = tweets[0]["text"]
    line_bot_api.reply_message(
        event_token,
        TextSendMessage(text=example_context))
    # 画像がある場合は画像もリプライ
    if len(tweets[0]["image"]) > 0:
        line_bot_api.reply_message(
            event_token,
            ImageSendMessage(original_content_url=tweets[0]["image"][0], preview_image_url=tweets[0]["image"][0]))

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
"""
