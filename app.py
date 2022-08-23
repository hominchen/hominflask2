from enum import unique
from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.config['SECRET_KEY'] = "secret key 123456987"

# === SQL ===
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# 'mysql://使用者名:密碼@url/資料庫名'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345678@localhost/our_users2'


db = SQLAlchemy(app)
migrate = Migrate(app, db)

#01 網站首頁
@app.route("/")
def index():
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

#05 使用者增加
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash加密
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            
            user = Users(name=form.name.data,
                    email=form.email.data,
                    favorite_color=form.favorite_color.data,
                    password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        
        name = form.name.data

        form.name.data = ""
        form.email.data = ""
        form.favorite_color.data = ""
        form.password_hash.data = ""
        flash('使用者新增成功！')
    
    # 查詢db
    our_users = Users.query.order_by(Users.date_added)

    return render_template("add_user.html",
        form=form,
        name=name,
        our_users=our_users
        )

#06 使用者更新
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form=UserForm()
    name_to_update=Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name=request.form['name']
        name_to_update.email=request.form['email']
        name_to_update.favorite_color=request.form['favorite_color']
        try:
            db.session.commit()
            flash('使用者已成功更新')
            return render_template('update.html',
                form=form,
                name_to_update=name_to_update
                )
        except:
            flash("看來有些問題，請再試試！")
            return render_template("update.html",
                form=form,
                name_to_update=name_to_update
                )
    else:
        return render_template("update.html",
            form=form,
            name_to_update=name_to_update,
            id=id)

#07 刪除
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('刪除資料成功')

        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html",
            form=form,
            name=name,
            our_users=our_users,
            id=id)
    except:
        flash('刪除使用者有錯誤，請再次確認。')
        return render_template("add_user.html",
            form=form,
            name=name,
            our_users=our_users,
            id=id)

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
    favorite_color = StringField("喜愛的顏色")
    password_hash = PasswordField('請輸入密碼', 
        validators=[DataRequired(), 
        EqualTo('password_hash2', message='密碼必須匹配')])
    # 驗證的密碼並不會被儲存到資料庫，用一個變量來承接
    password_hash2 = PasswordField('請再次輸入密碼', validators=[DataRequired()])
    submit = SubmitField("確認")

# ==== db model ====
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Hash password
    @property
    def password(self):
        raise AttributeError("哈希屬性不可讀取！")
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return '<Name %r>' % self.name



if __name__ == "__main__":
    app.run(debug=True, port=5000)
