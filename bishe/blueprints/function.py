# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect, url_for, \
    Blueprint, session, current_app, send_from_directory, request, Response
from flask_login import login_required, current_user
from bishe.forms import ApplyForm
from bishe.models import Apply, Student, Academic, Pass, School, Revoke
from bishe.extensions import db, bloomfilter
from bishe.utils import random_filename, redirect_back, getNewAddress, transaction, getInformation, cmp_json
from datetime import datetime
import os
import json

func_bp = Blueprint('function', __name__)


@func_bp.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    form = ApplyForm()
    if form.validate_on_submit():
        name = session['message']['name']
        school = form.school.data
        department = form.department.data
        major = form.major.data
        in_time = form.in_time.data
        out_time = form.out_time.data
        _type = form.type.data
        level = form.level.data
        year = form.year.data

        f = form.image.data
        filename = random_filename(f.filename)

        my_apply = Apply.query.filter_by(
            name=name,
            school=school,
            department=department,
            major=major,
            type=_type,
            level=level,
            year=year
        ).first()

        if my_apply and my_apply.apply_statue != 0:
            flash("待审核或已通过，请勿重复申请", "warning")
        else:
            my_apply = Apply(
                name=name,
                school=school,
                department=department,
                major=major,
                in_time=in_time,
                out_time=out_time,
                type=_type,
                level=level,
                year=year,
                apply_statue=2,
                image=filename,
                student=Student.query.get(current_user.seed)
            )

            db.session.add(my_apply)
            db.session.commit()

            f.save(os.path.join(current_app.config['IMAGE_SAVE_PATH'], filename))

            flash("申请成功,请等待审核", "info")
            return redirect(url_for('function.profile_apply', apply_id=my_apply.id))

    return render_template('function/apply.html', form=form, message=session['message'])


# 申请表信息
@func_bp.route('/profile_apply/<int:apply_id>')
@login_required
def profile_apply(apply_id):
    apply_table = Apply.query.get(apply_id)
    if current_user.role == '2':
        return render_template('function/check_apply.html', apply_table=apply_table)

    return render_template('function/profile_apply.html', apply_table=apply_table)


# 证书信息
@func_bp.route('/profile_academic/<string:hash_value>')
def profile_academic(hash_value):
    academic = Academic.query.get(hash_value)
    try:
        jsonData = getInformation(hash_value)
        academic_json = academic.to_json()

        believable = cmp_json(academic_json, jsonData)
    except:
        believable = False

    if current_user.is_authenticated and current_user.role == '2':
        return render_template('function/check_academic.html', academic=academic, believable=believable)

    return render_template('function/profile_academics.html', academic=academic, believable=believable)


@func_bp.route('/pass_confirm/<int:apply_id>', methods=['POST'])  # apply_table有属性未添加
@login_required
def pass_confirm(apply_id):
    if request.json:
        quest = request.json

    apply_table = Apply.query.get(apply_id)
    school = School.query.get(current_user.seed)

    student_seed = apply_table.student.seed
    current_add = getNewAddress(current_user.seed)
    print(current_add)
    pass_time = datetime.now()

    form = {
        "name": apply_table.name,
        "school": apply_table.school,
        "department": apply_table.department,
        "major": apply_table.major,
        "in_time": apply_table.in_time.strftime('%Y-%m-%d'),
        "out_time": apply_table.out_time.strftime('%Y-%m-%d'),
        "type": apply_table.type,
        "level": apply_table.level,
        "year": apply_table.year,
        "pass_time": pass_time.strftime('%Y-%m-%d'),
        "image": apply_table.image,
        "student_seed": student_seed,
        "dealer_seed": current_user.seed
    }

    hash_value = transaction(student_seed, current_add, form)
    print(hash_value)
    # hash_value = getNewSeed()
    remark = '于' + pass_time.strftime('%Y-%m-%d %H:%M:%S') + '由' + school.name + '确认通过<br>'

    pass_table = Pass(
        school=apply_table.school,
        pass_time=pass_time,
        dealer=school
    )

    academic = Academic(
        hash_value=hash_value,
        name=apply_table.name,
        school=apply_table.school,
        department=apply_table.department,
        major=apply_table.major,
        in_time=apply_table.in_time,
        out_time=apply_table.out_time,
        type=apply_table.type,
        level=apply_table.level,
        year=apply_table.year,
        status=1,
        image=apply_table.image,
        pass_time=pass_time,
        remark=remark,
        student=apply_table.student,
        pass_table=pass_table,
        dealer_seed=current_user.seed
    )

    db.session.add(pass_table)
    db.session.add(academic)

    apply_table.apply_statue = 1
    apply_table.dealer = school
    apply_table.deal_time = pass_time
    apply_table.remark = remark
    apply_table.hash_value = hash_value

    db.session.commit()

    bloomfilter.add(hash_value)

    flash('通过成功', 'success')
    return Response(json.dumps({'success': True}), mimetype='application/json')


@func_bp.route('/unpass_confirm/<int:apply_id>', methods=['POST'])
@login_required
def unpass_confirm(apply_id):
    if request.json is None:
        return Response(json.dumps({'success': False}), mimetype='application/json')

    quest = request.json
    try:
        reason = quest['reason']
    except:
        reason = ''

    if reason == '':
        reason = '未通过原因：无'
    else:
        reason = '未通过原因：' + reason

    unpass_time = datetime.now()
    reason = '于' + unpass_time.strftime('%Y-%m-%d %H:%M:%S') + '由' + session['message']['name'] + '不予通过<br>' + reason

    apply_table = Apply.query.get(apply_id)
    apply_table.apply_statue = 0
    apply_table.dealer = School.query.get(current_user.seed)
    apply_table.deal_time = unpass_time
    apply_table.remark = reason
    db.session.commit()

    flash('已确认该申请不通过', 'info')
    return Response(json.dumps({'success': True}), mimetype='application/json')


@func_bp.route('/revoke_confirm/<string:hash_value>', methods=['POST'])
@login_required
def revoke_confirm(hash_value):
    if request.json is None:
        return Response(json.dumps({'success': False}), mimetype='application/json')

    quest = request.json
    try:
        reason = quest['reason']
    except:
        reason = ''

    if reason == '':
        reason = '撤销原因：无<br>'
    else:
        reason = '撤销原因：' + reason + '<br>'

    revoke_time = datetime.now()
    reason = '于' + revoke_time.strftime('%Y-%m-%d %H:%M:%S') + '由' + session['message']['name'] + '撤销<br>' + reason

    academic = Academic.query.get(hash_value)
    academic.status = 0
    if academic.remark:
        academic.remark = academic.remark + reason
    else:
        academic.remark = reason

    revoke_table = Revoke(
        school=academic.school,
        revoke_time=revoke_time,
        reason=reason,
        dealer=School.query.get(current_user.seed),
        academic=academic
    )

    db.session.add(revoke_table)
    db.session.commit()

    flash('已撤销该证书', 'info')
    return Response(json.dumps({'success': True}), mimetype='application/json')


@func_bp.route('/recover_confirm/<string:hash_value>', methods=['POST'])
@login_required
def recover_confirm(hash_value):
    if request.json is None:
        return Response(json.dumps({'success': False}), mimetype='application/json')

    quest = request.json
    try:
        reason = quest['reason']
    except:
        reason = ''

    if reason == '':
        reason = '恢复原因：无<br>'
    else:
        reason = '恢复原因：' + reason + '<br>'

    recover_time = datetime.now()
    reason = '于' + recover_time.strftime('%Y-%m-%d %H:%M:%S') + '由' + session['message']['name'] + '恢复<br>' + reason

    academic = Academic.query.get(hash_value)
    academic.status = 1
    academic.remark = academic.remark + reason
    revoke_table = academic.revoke_table
    db.session.delete(revoke_table)
    db.session.commit()

    flash('已恢复该证书', 'info')
    return Response(json.dumps({'success': True}), mimetype='application/json')


# 获取图片
@func_bp.route('/get_image/<path:filename>')
def get_image(filename):
    return send_from_directory(current_app.config['IMAGE_SAVE_PATH'], filename)


@func_bp.route('/avatars/<path:filename>')
@login_required
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'], filename)


# 搜索
@func_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    if q == '':
        flash('请输入要查询的证书hash值/姓名/学校/学院/专业.', 'warning')
        return redirect_back()

    if len(q) == 81:
        if q in bloomfilter:
            return redirect(url_for('function.profile_academic', hash_value=q))
        else:
            if current_user.is_authenticated and current_user.role == '2':
                return render_template('function/check_academic.html', academic=None)
            return render_template('function/profile_academics.html', academic=None)

    category = request.args.get('category', 'academic')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['IOTA_SEARCH_RESULT_PER_PAGE']

    if category == 'apply' and current_user.is_authenticated and current_user.role == '2':
        pagination = Apply.query.filter_by(
            school=session['message']['organization']).whooshee_search(q).paginate(page, per_page)
    else:
        pagination = Academic.query.whooshee_search(q).paginate(page, per_page)

    results = pagination.items

    return render_template('function/search.html', q=q, results=results,
                           pagination=pagination, category=category)
