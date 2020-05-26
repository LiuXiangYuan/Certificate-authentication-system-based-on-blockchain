# -*- coding: utf-8 -*-

from flask_avatars import Avatars
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
from flask_whooshee import Whooshee
from pybloom_live import ScalableBloomFilter

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
ckeditor = CKEditor()
moment = Moment()
toolbar = DebugToolbarExtension()
migrate = Migrate()
avatars = Avatars()
whooshee = Whooshee()
bloomfilter = ScalableBloomFilter(initial_capacity=1000)


@login_manager.user_loader
def load_user(id):
    from bishe.models import User_auth
    user = User_auth.query.get(int(id))
    return user


login_manager.login_view = 'auth.login'
# login_manager.login_message = '欢迎'
# login_manager.login_message_category = 'warning'
