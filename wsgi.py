import os, sys
import flask
import sqlalchemy

# 自作したアプリケーションをインポートして実行できるようにする
from main import app as application

sys.path.append('/home/ubuntu/flask')