from enum import unique
from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = "secret key 123456987"

# === SQL ===
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# 'mysql://使用者名:密碼@url/資料庫名'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:12345678@localhost/our_users2'


db = SQLAlchemy(app)

#01 網站首頁
@app.route("/")
def index():
    # return "<h1>Hello World!<h1>"
    return render_template("index.html")

#02 使用者回傳
@app.route("/user")
def user():
    stuff = "這是<strong>粗體字</strong>"
    favorite_pizza = ["Pepperoni", "起司", "Mushrooms", 41]
    name= "bOb"
    return render_template("user.html", 
    user_name=name,
    stuff=stuff,
    favorite_pizza=favorite_pizza)

#04 Name
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data=""
        flash('表單提交成功')
    return render_template('name.html',
        name=name,
        form=form)

#05 Add User
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data,
                    email=form.email.data)
            # 儲存到資料表
            db.session.add(user)
            db.session.commit()
        
        name = form.name.data
        # 清除頁面
        form.name.data = ""
        form.email.data = ""
        flash('使用者新增成功！')
    
    # 查詢db
    our_users = Users.query.order_by(Users.date_added)

    return render_template("add_user.html",
        form=form,
        name=name,
        our_users=our_users)

#03 錯誤頁面
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

# ==== FlaskForm ====
class NamerForm(FlaskForm):
    name = StringField("請問你的名子？", validators=[DataRequired()])
    submit = SubmitField("確認")

class UserForm(FlaskForm):
    name = StringField("姓名", validators=[DataRequired()])
    email = StringField("信箱", validators=[DataRequired()])
    submit = SubmitField("確認")

# ==== db model ====
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return '<Name %r>' % self.name



if __name__ == "__main__":
    app.run(debug=True, port=5000)
