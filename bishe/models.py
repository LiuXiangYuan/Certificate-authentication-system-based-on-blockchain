# -*- coding: utf-8 -*-
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from bishe.extensions import db, whooshee
from datetime import datetime


class User_auth(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    seed = db.Column(db.String(100), unique=True, index=True)
    phone = db.Column(db.String(11), unique=True, index=True)
    email = db.Column(db.String(256), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(5), nullable=False)
    image = db.Column(db.String(64))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Student(db.Model):
    seed = db.Column(db.String(100), primary_key=True)
    address = db.Column(db.String(100))
    name = db.Column(db.String(20), nullable=False)

    apply_table = db.relationship('Apply', back_populates='student')
    academics = db.relationship('Academic', back_populates='student')
    blacklist = db.relationship('Blacklist', back_populates='student')


class School(db.Model):
    seed = db.Column(db.String(100), primary_key=True)
    address = db.Column(db.String(100))
    name = db.Column(db.String(20), nullable=False)
    organization = db.Column(db.String(64), nullable=True, default=None)

    pass_table = db.relationship('Pass', back_populates='dealer')
    revoke_table = db.relationship('Revoke', back_populates='dealer')
    apply_table = db.relationship('Apply', back_populates='dealer')


class Institution(db.Model):
    seed = db.Column(db.String(100), primary_key=True)
    address = db.Column(db.String(100))
    name = db.Column(db.String(20), nullable=False)
    organization = db.Column(db.String(64), nullable=True, default=None)

    blacklist = db.relationship('Blacklist', back_populates='dealer')


@whooshee.register_model('name', 'school', 'department', 'major')
class Apply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    school = db.Column(db.String(64))
    department = db.Column(db.String(64))
    major = db.Column(db.String(64))
    in_time = db.Column(db.Date)
    out_time = db.Column(db.Date)
    type = db.Column(db.String(64))
    level = db.Column(db.String(64))
    year = db.Column(db.String(10))
    apply_time = db.Column(db.DateTime, default=datetime.now)
    apply_statue = db.Column(db.Integer)  # 0未通过 1通过 2待审核
    image = db.Column(db.String(64))
    deal_time = db.Column(db.DateTime)
    remark = db.Column(db.Text)
    hash_value = db.Column(db.String(100))

    deal_seed = db.Column(db.String(100), db.ForeignKey('school.seed'))
    dealer = db.relationship('School', back_populates='apply_table')
    student_seed = db.Column(db.String(100), db.ForeignKey('student.seed'))
    student = db.relationship('Student', back_populates='apply_table')


class Pass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school = db.Column(db.String(64), nullable=True, default=None)
    pass_time = db.Column(db.DateTime, default=datetime.now)

    deal_seed = db.Column(db.String(100), db.ForeignKey('school.seed'))
    dealer = db.relationship('School', back_populates='pass_table')
    academic_hash = db.Column(db.String(100), db.ForeignKey('academic.hash_value'))
    academic = db.relationship('Academic')


class Revoke(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school = db.Column(db.String(64), nullable=True, default=None)
    revoke_time = db.Column(db.DateTime, default=datetime.now)
    reason = db.Column(db.Text)

    deal_seed = db.Column(db.String(100), db.ForeignKey('school.seed'))
    dealer = db.relationship('School', back_populates='revoke_table')
    academic_hash = db.Column(db.String(100), db.ForeignKey('academic.hash_value'))
    academic = db.relationship('Academic')


class Blacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deal_seed = db.Column(db.String(100), db.ForeignKey('institution.seed'))
    academic_hash = db.Column(db.String(100), db.ForeignKey('academic.hash_value'))
    student_seed = db.Column(db.String(100), db.ForeignKey('student.seed'))
    organization = db.Column(db.String(64), nullable=True, default=None)
    blacklist_time = db.Column(db.DateTime, default=datetime.now)
    reason = db.Column(db.Text)

    dealer = db.relationship('Institution', back_populates='blacklist')
    academic = db.relationship('Academic', back_populates='blacklist')
    student = db.relationship('Student', back_populates='blacklist')


@whooshee.register_model('hash_value', 'name', 'school', 'department', 'major')
class Academic(db.Model):
    hash_value = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(20))
    school = db.Column(db.String(64))
    department = db.Column(db.String(64))
    major = db.Column(db.String(64))
    in_time = db.Column(db.Date)
    out_time = db.Column(db.Date)
    type = db.Column(db.String(64))
    level = db.Column(db.String(64))
    year = db.Column(db.String(10))
    status = db.Column(db.Integer, default=1)
    pass_time = db.Column(db.DateTime, default=datetime.now)
    image = db.Column(db.String(64))
    remark = db.Column(db.Text)
    dealer_seed = db.Column(db.String(100))

    student_seed = db.Column(db.String(100), db.ForeignKey('student.seed'))
    student = db.relationship('Student', back_populates='academics')
    pass_table = db.relationship('Pass', uselist=False, cascade='all, delete-orphan')
    revoke_table = db.relationship('Revoke', uselist=False, cascade='all, delete-orphan')
    blacklist = db.relationship('Blacklist', back_populates='academic')

    def to_json(self):
        jsonData = {
            "name": self.name,
            "school": self.school,
            "department": self.department,
            "major": self.major,
            "in_time": self.in_time.strftime('%Y-%m-%d'),
            "out_time": self.out_time.strftime('%Y-%m-%d'),
            "type": self.type,
            "level": self.level,
            "year": self.year,
            "pass_time": self.pass_time.strftime('%Y-%m-%d'),
            "image": self.image,
            "student_seed": self.student_seed,
            "dealer_seed": self.dealer_seed
        }

        return jsonData
