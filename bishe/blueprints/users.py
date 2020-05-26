# -*- coding: utf-8 -*-

from flask import render_template, flash, Blueprint, session, \
    request, Response, redirect, url_for, current_app
from flask_login import login_required, current_user, logout_user
from bishe.models import User_auth, Student, Apply, Academic, School, Pass, Revoke
import json
import traceback

from bishe.extensions import db

users_bp = Blueprint('users', __name__)


@users_bp.route('/cv', methods=['GET', 'POST'])
@login_required
def cv():
    if current_user.role == "1":  # Student
        user = Student.query.get(current_user.seed)
        academics = user.academics
        apply_tables = user.apply_table
        return render_template('users/cv.html', message=session['message'], academics=academics,
                               apply_tables=apply_tables)
    elif current_user.role == "2":  # School
        user = School.query.get(current_user.seed)
        apply_tables = user.apply_table
        pass_academics = Academic.query.filter_by(dealer_seed=current_user.seed, status=1).all()
        revoke_tables = user.revoke_table
        return render_template('users/cv.html', message=session['message'], apply_tables=apply_tables,
                               pass_academics=pass_academics, revoke_tables=revoke_tables)
    else:
        return render_template('users/cv.html', message=session['message'])


@users_bp.route('/myapply')
@login_required
def myapply():
    if current_user.role != "1":
        flash("你无权访问该页面", "warning")
        redirect(url_for('homepage.index'))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['IOTA_LIST_PER_PAGE']
    pagination = Apply.query.filter_by(student_seed=current_user.seed).paginate(page, per_page)
    apply_tables = pagination.items
    return render_template('users/apply_tables.html', apply_tables=apply_tables,
                           title='我的申请表', pagination=pagination)


@users_bp.route('/myacademic')
@login_required
def myacademic():
    if current_user.role != "1":
        flash("你无权访问该页面", "warning")
        redirect(url_for('homepage.index'))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['IOTA_LIST_PER_PAGE']
    pagination = Academic.query.filter_by(student_seed=current_user.seed).paginate(page, per_page)
    academics = pagination.items
    return render_template('users/academics.html', academics=academics,
                           title='我的证书', pagination=pagination)


@users_bp.route('/wait_deal')
@login_required
def wait_deal():
    if current_user.role != "2":
        flash("你无权访问该页面", "warning")
        redirect(url_for('homepage.index'))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['IOTA_LIST_PER_PAGE']
    pagination = Apply.query.filter_by(school=session['message']['organization'],
                                         apply_statue=2).order_by("apply_time").paginate(page, per_page)
    apply_tables = pagination.items
    return render_template('users/apply_tables.html', apply_tables=apply_tables,
                           title='待处理申请表', isnone='暂未有待处理申请表信息', pagination=pagination)


@users_bp.route('/have_deal')
@login_required
def have_deal():
    if current_user.role != "2":
        flash("你无权访问该页面", "warning")
        redirect(url_for('homepage.index'))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['IOTA_LIST_PER_PAGE']
    pagination = Apply.query.filter(
                    Apply.school == session['message']['organization']
                ).filter(
                    db.or_(Apply.apply_statue == 0, Apply.apply_statue == 1)
                ).order_by("apply_time").paginate(page, per_page)
    apply_tables = pagination.items
    return render_template('users/apply_tables.html', apply_tables=apply_tables,
                           title='已处理申请表', isnone='暂未有已处理申请表信息', pagination=pagination)


@users_bp.route('/pass_academics')
@login_required
def pass_academics():
    if current_user.role != "2":
        flash("你无权访问该页面", "warning")
        redirect(url_for('homepage.index'))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['IOTA_LIST_PER_PAGE']
    pagination = Academic.query.filter_by(school=session['message']['organization'],
                                          status=1).paginate(page, per_page)
    academics = pagination.items
    return render_template('users/academics.html', academics=academics,
                           title='已允许通过的学历证书', isnone='暂未有允许通过的学历证书', pagination=pagination)


@users_bp.route('/revoke_academics')
@login_required
def revoke_academics():
    if current_user.role != "2":
        flash("你无权访问该页面", "warning")
        redirect(url_for('homepage.index'))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['IOTA_LIST_PER_PAGE']
    pagination = Academic.query.filter_by(school=session['message']['organization'],
                                          status=0).paginate(page, per_page)
    academics = pagination.items
    return render_template('users/academics.html', academics=academics,
                           title='撤销的学历证书', isnone='暂未有撤销的学历证书', pagination=pagination)


@users_bp.route('/update', methods=['POST'])
@login_required
def update():
    if request.json is None:
        return Response(json.dumps({'success': False, 'message': '参数错误，请检查客户端版本', 'code': 1}),
                        mimetype='application/json')
    quest = request.json
    try:
        try:
            phone = quest['phone']
        except:
            phone = ''
        try:
            email = quest['email']
        except:
            email = ''
        try:
            passwd = quest['password']
        except:
            passwd = ''

        if phone != '':
            if User_auth.query.filter_by(phone=phone).first():
                return Response(json.dumps({'success': False, 'message': '电话号码已被占用', 'code': 3}),
                                mimetype='application/json')
            current_user.phone = phone
        if email != '':
            if User_auth.query.filter_by(email=email).first():
                return Response(json.dumps({'success': False, 'message': '邮箱已被占用', 'code': 3}),
                                mimetype='application/json')
            current_user.email = email
        if passwd != '':
            if len(passwd) < 10:
                return Response(json.dumps({'success': False, 'message': '密码过短', 'code': 4}),
                                mimetype='application/json')
            current_user.set_password(passwd)

        db.session.commit()

        if passwd != '':
            flash("密码已修改，请重新登录", 'info')
            logout_user()
        else:
            flash("更新成功", "info")
        return Response(json.dumps({'success': True, 'message': '成功', 'code': 0}), mimetype='application/json')
    except BaseException as e:
        traceback.print_exc()
        print(e)
        return Response(json.dumps({'success': False, 'message': '服务器端发生错误', 'code': 1}), mimetype='application/json')