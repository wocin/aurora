# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask.ext.login import LoginManager
login_manager = LoginManager()

from flask.ext.debugtoolbar import DebugToolbarExtension
debugtoolbar = DebugToolbarExtension

from flask.ext.gravatar import Gravatar
gravatar = Gravatar(default='identicon', rating='g')
