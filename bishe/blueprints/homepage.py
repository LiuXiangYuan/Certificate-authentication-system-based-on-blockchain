# -*- coding: utf-8 -*-

from flask import render_template, Blueprint
from flask_login import current_user
from bishe.extensions import bloomfilter
from bishe.models import Academic


homepage_bp = Blueprint('homepage', __name__)


@homepage_bp.before_app_first_request
def load_academics():
    academics = Academic.query.all()
    for academic in academics:
        bloomfilter.add(academic.hash_value)
    print('加入证书数量：'+str(len(bloomfilter)))


@homepage_bp.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('function/index.html')
    return render_template('homepage/index.html')
