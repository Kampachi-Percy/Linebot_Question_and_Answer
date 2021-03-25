# event.messageはjson形式で渡される
# 詳細は https://developers.line.biz/ja/reference/messaging-api を参照
# スタンプIDは https://developers.line.biz/media/messaging-api/sticker_list.pdf を参照

from database_wrapper import User, Question, session
from sqlalchemy.sql.expression import func

doc_post = "投稿モードを開始します\n\n\
詳しい書き方はこちら\n\
https://qiita.com/Kampachi_/private/38d178e17fc1d77b2edf"
doc_qa = "一問一答モード(β版)"
doc_free = "終了しました"

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
    if "hello" in message:
        return "good morning!"
    if "おはよう" in message:
        return "おはよう！いいてんきだね"
    if "🐡( '-' 🐡  )ﾌｸﾞﾊﾟﾝﾁ" in message:
        return "ぐおお"

    if message == "投稿" and user.status != "post":
        user.status = "post"
        session.commit()
        return doc_post
    
    if message == "一問一答" and user.status != "qa":
        user.status = "qa"
        session.commit()
        return doc_qa

    if message == "終了" and user.status != "free":
        user.status = "free"
        session.commit()
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

def solve(event, user) -> str:

    # このあたりでジャンル選択をする
    if user.question_number == 0:
        user_question_number = 1

    present_question = session.query(Question).filter(Question.question_id==user.question_number).first()
    next_question = session.query(Question).order_by(func.random()).first()

    if event.message.text == present_question.answer:
        reply = "正解！\n"
        user.otetsuki_counter = 0
        user.question_number = next_question.question_id
        session.commit()
        reply += next_question.question
    else:
        user.otetsuki_counter += 1
        if user.otetsuki_counter >= 3:
            reply = f"不正解！正解は\n{present_question.answer}\nでした\n\n"
            user.otetsuki_counter = 0
            user.question_number = next_question.question_id
            reply += next_question.question
        else:
            reply = f"不正解！お手つき{user.otetsuki_counter}/3\n"
            reply += present_question.question
        session.commit()
    
    return reply