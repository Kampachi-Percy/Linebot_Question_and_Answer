from flask import Flask, render_template, request, abort
import os

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import LineBotApiError, InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, StickerMessage, ImageMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction

import config, replier

app = Flask(__name__)

line_bot_api = LineBotApi(config.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.CHANNEL_SECRET)

# ブラウザ上で見える画面
@app.route('/')
def index():
    return render_template("index.html")

@app.route("/callback", methods=['POST'])
def callback(): # Webhookからのリクエストをチェックする
    
    # HTTPリクエストヘッダから署名検証のための値を取得
    signature = request.headers['X-Line-Signature']

    # postされたデータを受け取る
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 署名を検証し, 問題なければhandleに定義されている関数を呼び出す
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# メッセージが来たときの反応
@handler.add(MessageEvent, message=[TextMessage, StickerMessage, ImageMessage])
def handle_message(event):
    reply = replier.reply(event, line_bot_api)
    # event.reply_token: イベントの応答に用いるトークン
    # TextSendMessage: 返信用のオブジェクト
    messages = TextSendMessage(text=reply)
    line_bot_api.reply_message(event.reply_token, messages=messages)
    # language_list = ["Ruby", "Python", "PHP", "Java", "C"]

    # items = [QuickReplyButton(action=MessageAction(label=f"{language}", text=f"{language}が好き")) for language in language_list]

    # messages = TextSendMessage(text="どの言語が好きですか？",
    #                            quick_reply=QuickReply(items=items))

    # line_bot_api.reply_message(event.reply_token, messages=messages)


if __name__ == '__main__':
    app.run(debug=True)