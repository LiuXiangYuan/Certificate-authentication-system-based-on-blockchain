# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, SelectField, BooleanField, PasswordField, DateField, RadioField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    username = StringField('Seed/邮箱/手机号', validators=[DataRequired(), Length(1, 100)])
    password = PasswordField('密码', validators=[DataRequired(), Length(1, 128)])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')


class RegisterForm(FlaskForm):
    name = StringField(u'姓名', validators=[DataRequired(), Length(1, 20)])
    phone = StringField(u'手机号', validators=[DataRequired()])
    email = StringField(u'邮箱', validators=[DataRequired(), Email(), Length(1, 256)])
    password = PasswordField(u'密码', validators=[DataRequired(), Length(1, 128)])
    password_2 = PasswordField(u'再次输入密码', validators=[DataRequired(), Length(1, 128)])
    role = RadioField(u'身份', choices=[("1", u'学生'), ("2", u'校方机构')], default="1")
    organization = StringField(u'校名/机构名', validators=[DataRequired()], default=u"校名/机构名")
    submit = SubmitField('注册')


class ApplyForm(FlaskForm):
    image = FileField('个人照片', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], '文件只允许上传 .jpg/.png/.jpeg')
    ])
    school = StringField('学校', validators=[DataRequired(), Length(4, 64)])
    department = StringField('学院', validators=[DataRequired(), Length(4, 64)])
    major = StringField('专业', validators=[DataRequired(), Length(3, 64)])
    in_time = DateField('入学时间', validators=[DataRequired()], format='%Y-%m-%d')
    out_time = DateField('毕业时间', validators=[DataRequired()], format='%Y-%m-%d')
    type = SelectField('学历类型', validators=[DataRequired('请选择学历类型')],
                       choices=[("全日制普通本科", "全日制普通本科"), ("全日制普通第二学士学位", "全日制普通第二学士学位"),
                                ("全日制普通专科(高职)", "全日制普通专科(高职)"), ("全日制普通硕士学位研究生", "全日制普通硕士学位研究生"),
                                ("非全日制普通硕士学位研究生", "非全日制普通硕士学位研究生"), ("全日制普通博士学位研究生", "全日制普通博士学位研究生"),
                                ("成人教育大类", "成人教育大类")])
    level = SelectField('学历层次', validators=[DataRequired('请选择学历层次')],
                        choices=[("专科", "专科"), ("本科", "本科"), ("硕士研究生", "硕士研究生"), ("博士研究生", "博士研究生"),
                                 ("第二学士学位班", "第二学士学位班")])
    year = SelectField('学制', validators=[DataRequired('请选择学制')],
                       choices=[("1年", "1年"), ("2年", "2年"), ("3年", "3年"),
                                ("4年", "4年"), ("5年", "5年"), ("6年", "6年"),
                                ("7年", "7年"), ("8年", "8年")])
    submit = SubmitField('提交')


class ModifyForm(FlaskForm):
    phone = StringField(u'手机号', validators=[DataRequired()])
    email = StringField(u'邮箱', validators=[DataRequired(), Email(), Length(1, 256)])
    password = PasswordField(u'密码', validators=[DataRequired(), Length(1, 128)])
    password_2 = PasswordField(u'再次输入密码', validators=[DataRequired(), Length(1, 128)])
    submit = SubmitField()
