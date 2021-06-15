import os
from flask import Markup
from markdown import markdown

from icecream import ic

def read_md(filename):
    with open(f"/home/ubuntu/flask/markdown/mathterro/{filename}.md", encoding="utf-8") as mdfile:
        mdcontent = mdfile.read()
    return Markup(markdown(mdcontent))

ALLOWED_EXTENTIONS = set(["png", "jpg", "jpeg", "pdf", "gif"])

def is_img(filename) -> bool: # 拡張子の確認
    return "." in filename and filename.split(".")[-1].lower() in ALLOWED_EXTENTIONS

ic(is_img("test.png"))