import os
import datetime
from flask import Flask, render_template, request, abort, redirect, url_for, flash
from flask import send_from_directory, session, Markup
from werkzeug.utils import secure_filename

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import LineBotApiError, InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, StickerMessage, ImageMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction

import config, replier
from markdown_wrapper import read_md

app = Flask(__name__)
app.secret_key = config.FLASK_SECRET_KEY

def is_img(filename):  # 拡張子の確認
    ALLOWED_EXTENTIONS = set(["png", "jpg", "jpeg", "pdf", "gif"])
    return "." in filename and filename.split(".")[-1].lower() in ALLOWED_EXTENTIONS


# ブラウザ上で見える画面
@app.route('/')
def index():
    return render_template("index.html", title="TOP")

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, "static/img"), "favicon.ico")

@app.route("/mathterro", methods=["GET", "POST"])
def mathterro():
    tasks = os.listdir(os.path.join("/home/ubuntu/flask/markdown", "mathterro"))
    for i in range(len(tasks)):
        tasks[i] = tasks[i].split(".")[0]
    tasks.sort()
    return render_template("mathterro.html", title="数テロ改", tasks=tasks)

@app.route("/mathterro/<task>", methods=["GET", "POST"])
def show_md(task):
    mdfile_path = f"/home/ubuntu/flask/markdown/mathterro/{task}.md"
    content = read_md(mdfile_path)

    # ここあとからまとめる
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)

        if filename == "":
            flash("ファイルが選択されていません")
            return redirect(request.url)
        
        if is_img(file.filename) == False:
            flash("対応していないファイル形式です")
            return redirect(request.url)
        
        extention = filename.split(".")[-1].lower()
        dt_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = dt_now + "." + extention
        file.save(os.path.join("/home/ubuntu/flask/uploads", filename))
        flash("提出完了しました！")
        return redirect(request.url)

    return render_template("md.html", title=task, md=content)

@app.route("/linebot_qa")
def linebot_qa():
    return render_template("linebot_qa.html", title="LINEBot")


# LINEBot

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

line_bot_api = LineBotApi(config.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.CHANNEL_SECRET)

# メッセージが来たときの反応
@handler.add(MessageEvent, message=[TextMessage, StickerMessage, ImageMessage])
def handle_message(event):
    reply = replier.reply(event, line_bot_api)
    # event.reply_token: イベントの応答に用いるトークン
    # TextSendMessage: 返信用のオブジェクト

    # あまりやりたくないが type(reply) の型によって分岐する
    if type(reply) == str:
        messages = TextSendMessage(text=reply)
    elif type(reply) == list:
        messages = TextSendMessage(text=reply[0], quick_reply=QuickReply(items=reply[1]))
    line_bot_api.reply_message(event.reply_token, messages=messages)


if __name__ == '__main__':
    app.run(debug=True)