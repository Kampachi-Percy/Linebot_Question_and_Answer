# event.messageはjson形式で渡される
# 詳細は https://developers.line.biz/ja/reference/messaging-api を参照
# スタンプIDは https://developers.line.biz/media/messaging-api/sticker_list.pdf を参照

from database_wrapper import User, Question, session
from sqlalchemy import distinct
from sqlalchemy.sql.expression import func
from linebot.models import QuickReply, QuickReplyButton, MessageAction
import itertools


def reply(event, line_bot_api) -> str:
    user_id = event.source.user_id
    user = session.query(User).filter(User.user_id==user_id).first()

    # 初回のみ登録作業
    if user is None:
        profile = line_bot_api.get_profile(user_id)
        new_user = User(user_id=user_id, user_name=profile.display_name)
        session.add(new_user)
        session.commit()
        user = session.query(User).filter(User.user_id==user_id).first()
    
    # スタンプを判別
    if event.message.type == "sticker":
        reply = "スタンプ"
        return reply

    # 画像を判別
    if event.message.type == "image":
        reply = "画像"
        return reply

    message = event.message.text
    if message == "status":
        return user.status
    if message == "help":
        return "https://qiita.com/Kampachi_/private/38d178e17fc1d77b2edf"
    if "hello" in message:
        return "good morning!"
    if "おはよう" in message:
        return "おはよう！いいてんきだね"
    if "🐡( '-' 🐡  )ﾌｸﾞﾊﾟﾝﾁ" in message:
        return "ぐおお"

    if message == "投稿" and user.status != "post":
        user.status = "post"
        session.commit()
        doc_post = "投稿モードを開始します\nhttps://qiita.com/Kampachi_/private/38d178e17fc1d77b2edf"
        return doc_post
    
    if message == "一問一答" and user.status != "qa":
        user.status = "qa"
        session.commit()
        reply = solve(event, user)
        return reply

    if message == "終了" and user.status != "free":
        user.status = "free"
        user.question_number = 0
        user.question_genre = "未選択"
        session.commit()
        doc_free = "終了しました"
        return doc_free

    if user.status == "post":
        reply = post(event, user)
        return reply

    if user.status == "qa":
        reply = solve(event, user)
        return reply
    
    # なにもなければオウム返しする
    reply = event.message.text
    return reply


def post(event, user) -> str:
    message = event.message.text
    if message.count("\n") == 2:
        m = message.split("\n")
        new_question = Question(genre=m[0], question=m[1], answer=m[2], author=user.user_id)
        session.add(new_question)
        session.commit()
        reply = "登録しました！"
    else:
        reply = "改行の数が合っていません"
    return reply

def solve(event, user):

    # 一問一答モードに入ったときのジャンル選択
    if user.question_genre == "未選択":
        # 重複なしでジャンルを取得する
        genres_tuple = session.query(Question.genre).distinct(Question.genre).all()
        # タプルで返ってくるのを配列に整形する
        genres_list = list(itertools.chain.from_iterable(genres_tuple))

        # クイックリプライでうまくジャンルを選択できたら問題を出題する
        if event.message.text in genres_list:
            user.question_genre = event.message.text
            reply = next(user)
            session.commit()
            return reply
        else: # ジャンルが選択されていなければ, クイックリプライを表示するためのリストを返す
            genre_choice_text = "一問一答モード\nジャンルを選択してください"
            items = [QuickReplyButton(action=MessageAction(label=genre, text=genre)) for genre in genres_list]
            return [genre_choice_text, items]


    # 出題された問題の回答に対する処理
    present_question = session.query(Question).filter(Question.question_id==user.question_number).first()

    if event.message.text == present_question.answer: # 正解
        present_question.correct_count += 1
        user.otetsuki_counter = 0
        reply = "正解！\n" + next(user)
    elif event.message.text == "パス": # パス
        user.otetsuki_counter = 0
        reply = f"正解は\n{present_question.answer}\nでした\n\n" + next(user)
    else:
        user.otetsuki_counter += 1
        if user.otetsuki_counter >= 3: # 3回連続不正解
            user.otetsuki_counter = 0
            reply = f"不正解！正解は\n{present_question.answer}\nでした\n\n" + next(user)
        else: # 不正解
            reply = f"不正解！お手つき{user.otetsuki_counter}/3\n"
            reply += present_question.question
    
    session.commit()
    return reply

def next(user) -> str: # 次の問題を出題する関数
    next_question = session.query(Question).filter(Question.genre==user.question_genre).order_by(func.random()).first()
    user.question_number = next_question.question_id
    next_question.asked_count += 1
    reply = f"問題No.{next_question.question_id}\n{next_question.question}"
    return reply