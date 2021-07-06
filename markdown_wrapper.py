import os
from flask import Markup
from markdown import markdown

def read_md(mdfile_path):
    with open(mdfile_path, encoding="utf-8") as mdfile:
        mdcontent = mdfile.read()
    return Markup(markdown(mdcontent, extensions=['extra']))