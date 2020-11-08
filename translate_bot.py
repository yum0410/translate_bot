from flask import Flask, request, abort
import os

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

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
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)



"""
heroku config:set YOUR_CHANNEL_SECRET="912d09c8e56a29388bfd2f8ca723ee88" --app translater-bot-202011
heroku config:set YOUR_CHANNEL_ACCESS_TOKEN="hFwz/Zpm4dPitmEGiQEe6067phDjC4i9u3hBvsHwFk/TLSZ5C9Hygj4E8ZL1I+P+pchR2KFUUwOvTu+kK2e+BlWeLT72/+wPjZ5q5LMiOmJQ4gtxRrGncEqcuL0ZovOdJugzDvXGPqj/8/aj5FsVhwdB04t89/1O/w1cDnyilFU=" --app translater-bot-202011
"""
