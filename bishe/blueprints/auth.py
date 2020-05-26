# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect, url_for, Blueprint, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_avatars import Identicon

from bishe.forms import LoginForm, RegisterForm
from bishe.models import User_auth, Student, School, Institution
from bishe.utils import judge_seed, judge_phone, judge_email, getNewSeed, random_avatar
from bishe.extensions import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('homepage.index'))

    form = LoginForm()
    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data
        remember = form.remember.data

        if judge_seed(username):
            user = User_auth.query.filter_by(seed=username).first()
        elif judge_email(username):
            user = User_auth.query.filter_by(email=username).first()
        elif judge_phone(username):
            user = User_auth.query.filter_by(phone=username).first()
        else:
            flash('用户名不正确，需为81位Seed或邮箱或手机号', 'warning')
            return render_template('auth/login.html', form=form)

        if user:
            if user.validate_password(password):
                login_user(user, remember)

                if user.role == "1":
                    user_message = Student.query.get(user.seed)
                    message = {'name': user_message.name}
                    session['message'] = message
                elif user.role == "2":
                    user_message = School.query.get(user.seed)
                    message = {'name': user_message.name, 'organization': user_message.organization}
                    session['message'] = message
                elif user.role == "3":
                    user_message = Institution.query.get(user.seed)
                    message = {'name': user_message.name, 'organization': user_message.organization}
                    session['message'] = message

                return redirect(url_for('homepage.index'))
            flash('用户名或密码错误', 'warning')
        else:
            flash('用户名不存在', 'warning')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('homepage.index'))

    form = RegisterForm()

    if form.validate_on_submit():
        name = form.name.data
        phone = str(form.phone.data)
        email = form.email.data
        password = form.password.data
        role = form.role.data
        organization = form.organization.data


        check_email = User_auth.query.filter_by(email=email).first()
        if check_email:
            flash('该邮箱已被注册，请尝试直接登录', 'warning')
            return render_template('auth/register.html', form=form)

        check_phone = User_auth.query.filter_by(phone=phone).first()
        if check_phone:
            flash('该号码已被注册，请尝试直接登录', 'warning')
            return render_template('auth/register.html', form=form)

        if role != 0 and organization is None:
            flash('校名/机构名不能为空！', 'warning')
            return render_template('auth/register.html', form=form)

        seed = getNewSeed()
        avatar = Identicon()
        filenames = avatar.generate(text=random_avatar())[2]

        user_auth = User_auth(
            seed=seed,
            phone=phone,
            email=email,
            role=role,
            image=filenames
        )
        user_auth.set_password(password)
        db.session.add(user_auth)

        if role == "1":#Student
            user = Student(
                seed=seed,
                name=name
            )
            db.session.add(user)
        elif role == "2":#School
            user = School(
                seed=seed,
                name=name,
                organization=organization
            )
            db.session.add(user)
        elif role == "3":#Institution
            user = Institution(
                seed=seed,
                name=name,
                organization=organization
            )
            db.session.add(user)

        db.session.commit()

        message = '注册成功，你的Seed为：'+seed+'，请妥善保管'
        flash(message, 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('homepage/index.html')
