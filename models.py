from app import db ,migrate,login_manager,search
from flask_login import UserMixin, AnonymousUserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime,timezone
from flask_sqlalchemy import event
from slugify import slugify
from flask import current_app
from flask_admin.contrib.sqla import ModelView
import os
from dotenv import load_dotenv
load_dotenv()


# from app import db,login_manager

class Permission:
    COMMENT = 0x02
    WRITE= 0x04
    MODERATE= 0x08
    ADMIN = 0x80
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role',lazy=True)

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0    
    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit() 

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm    
    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm    
    def reset_permissions(self):
        self.permissions = 0    
    def has_permission(self, perm):
        return self.permissions & perm == perm 


    def __repr__(self):
        return '<Role %r>' % self.name

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, nullable=False, index=True)
    pwd = db.Column(db.String(72), nullable=False, unique=True)
    uname = db.Column(db.String(20), nullable=False)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow) 
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable = False)


    def __init__(self, **kwargs):
    	super(User, self).__init__(**kwargs)
    	if self.role is None:
    		# check if the new user is set up as the admin, and gives them admin permissions
    		if self.email == os.getenv("ADMIN_EMAIL"):
    			self.role = Role.query.filter_by(permissions=0xff).first()
    		if self.role is None:
    			self.role = Role.query.filter_by(default=True).first()

    def can(self, permissions):
        return self.role is not None and \
        (self.role.permissions & permissions) == permissions
    def is_administrator(self):
        return self.can(Permission.ADMIN)
        
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  

class AnonymousUser(AnonymousUserMixin):
	def can(self, permissions):
		return False

	def is_administrator(self):
		return False

login_manager.anonymous_user = AnonymousUser


class Trucks(db.Model):
    __tablename__ = "trucks"

    id = db.Column(db.Integer, primary_key=True)
    regno = db.Column(db.String(100), nullable=False)
    truck_img = db.Column(db.String(150), default="no-image.jpg")
    size = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    owner = db.relationship("User", backref=db.backref("owner"), lazy=True)
    status = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "<Post %r>" % self.regno

class HiredTrucks(db.Model):
    __tablename__ = "hired_trucks"

    id = db.Column(db.Integer, primary_key=True)

    id_no = db.Column(db.String(8), unique=True, nullable=False, index=True)
    phone_no = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.String(20), nullable=False)
    date_of_hire = db.Column(db.DateTime(), default=datetime.utcnow)

    truck_id = db.Column(db.Integer, db.ForeignKey("trucks.id"), nullable=False)
    truck = db.relationship("Trucks", backref=db.backref("truck"), lazy=True)

    status = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "<Post %r>" % self.id_no

