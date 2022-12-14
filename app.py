from enum import unique
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import NamerForm, UserForm, PasswordForm, PostForm, LoginForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import os
import uuid as uuid

app = Flask(__name__)
ckeditor = CKEditor(app)

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = "secret key 123456987"

# === SQL ===
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# 'mysql://使用者名:密碼@url/資料庫名'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345678@localhost/our_users2'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://nlmjjobjxanlsu:4dc44cb4b7478a42df2f2fe81acc1968d1365c3b72161040db3b6c753fc34769@ec2-44-210-36-247.compute-1.amazonaws.com:5432/d7rsj34hduvmqm'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#11-3 login manager登入管理器
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
#11-1 login登入
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('登入成功')
                return redirect(url_for('dashboard'))
            else:
                flash('你的密碼錯誤！')
        else:
            flash('帳號似乎不存在...')
    return render_template('login.html', form=form)
#11-2 Dashboard個人資訊
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name=request.form['name']
        name_to_update.email=request.form['email']
        name_to_update.favorite_color=request.form['favorite_color']
        name_to_update.username=request.form['username']
        name_to_update.about_author=request.form['about_author']

        # 確認是否有上傳圖片
        if request.files['profile_pic']:
            name_to_update.profile_pic = request.files['profile_pic']
            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            # save img
            name_to_update.profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            # file to string
            name_to_update.profile_pic = pic_name
            try:
                db.session.commit()
                flash('使用者已成功更新')
                return render_template('dashboard.html',
                    form=form,
                    name_to_update=name_to_update)
            except:
                flash("看來有些問題，請再試試！")
                return render_template("dashboard.html",
                    form=form,
                    name_to_update=name_to_update)
        else:
            db.session.commit()
            flash('使用者已成功更新')
            return render_template('dashboard.html',
                form=form,
                name_to_update=name_to_update)
    else:
        return render_template("dashboard.html",
            form=form,
            name_to_update=name_to_update,
            id=id)

#11-4 logout登出
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('成功登出！')
    return redirect(url_for('login'))

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

#05-1 使用者增加
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    email = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash加密
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            
            user = Users(name=form.name.data,
                    username = form.username.data,
                    email=form.email.data,
                    favorite_color=form.favorite_color.data,
                    password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        
        # name = form.name.data

        form.name.data = ""
        form.username.data = ""
        form.email.data = ""
        form.favorite_color.data = ""
        form.password_hash.data = ""
        flash('使用者新增成功！')
    
    # 查詢db
    our_users = Users.query.order_by(Users.date_added)

    return render_template("add_user.html",
        form=form,
        email=email,
        our_users=our_users
        )
#05-2 使用者更新
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form=UserForm()
    name_to_update=Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name=request.form['name']
        name_to_update.email=request.form['email']
        name_to_update.favorite_color=request.form['favorite_color']
        name_to_update.username=request.form['username']
        try:
            db.session.commit()
            flash('使用者已成功更新')
            return render_template('update.html',
                form=form,
                name_to_update=name_to_update,
                id=id
                )
        except:
            flash("看來有些問題，請再試試！")
            return render_template("update.html",
                form=form,
                name_to_update=name_to_update,
                id=id
                )
    else:
        return render_template("update.html",
            form=form,
            name_to_update=name_to_update,
            id=id)
#05-3 刪除使用者
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if id == current_user.id:
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
    else:
        flash('抱歉！你沒有相關權限...')
        return redirect(url_for('dashboard'))
#05-4 Hash相符測試
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    # 需要創建PasswordForm的表單
    form = PasswordForm()
     
    # 驗證表單
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # 將表單內容清除
        form.email.data = ''
        form.password_hash.data = ''
        # 加入表單提交成功的flash功能
        flash('表單提交成功')        
        pw_to_check = Users.query.filter_by(email=email).first()
        passed = check_password_hash(pw_to_check.password_hash, password)
    return render_template("test_pw.html",
        email = email,
        password = password,
        pw_to_check = pw_to_check,
        passed = passed,
        form = form)

#09 JSON
@app.route('/date')
def get_current_date():
    favorite_pizza = {
        "Bob":"臘腸",
        "Kenny": "Cheese",
        "Mary": "Mushroom"
    }
    return favorite_pizza
    # return {'Date': date.today()}

#10-1 Post
@app.route('/add-post', methods=['GET', 'POST'])
# @login_required
def add_post():
    form=PostForm()
    if form.validate_on_submit():
        # foreign key
        poster = current_user.id
        post = Posts(
            title=form.title.data, 
            content=form.content.data, 
            # author=form.author.data, 
            poster_id=poster,
            slug=form.slug.data
            )
        form.title.data = ""
        form.content.data = ""
        # form.author.data = ""
        form.slug.data = ""
        db.session.add(post)
        db.session.commit()
        flash("Blog 訊息張貼成功")
    return render_template("add_post.html", form=form)
#10-2 Posts文章集
@app.route('/posts')
# @login_required
def posts():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)
#10-3 post內文
@app.route('/posts/<int:id>')
@login_required
def post(id):
    post=Posts.query.get_or_404(id)
    return render_template('post.html', post=post)
#10-4 edit文章編輯
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        # post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        db.session.add(post)
        db.session.commit()
        flash('文章已更新成功！')
        return redirect(url_for('post', id=post.id))
    # 作者id比對
    if current_user.id == post.poster_id or current_user.id == 1:
        form.title.data = post.title
        # form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash('你不是作者，無權編輯！')
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)

#10-5 delete刪除
@app.route('/post/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.id or id == 1:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash('內容已被刪除！')
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
        except:
            flash('內容無法刪除...')
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
    else:
        flash('你沒有權利刪除...')
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)

#12 admin管理者頁面
@app.route('/admin')
def admin():
    id = current_user.id
    if id == 1:
        return render_template('admin.html')
    else:
        flash('抱歉！ 你沒有相關權限...')
    return redirect(url_for('dashboard'))

#13 search檢索
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        post.searched = form.searched.data
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template("search.html", 
            form=form,
            searched=post.searched,
            posts = posts)

@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

#03 錯誤頁面
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500



# ==== db model ====
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    about_author = db.Column(db.Text())
    password_hash = db.Column(db.String(128))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # relationship - send 暗號'poster'給Posts的db
    posts = db.relationship('Posts', backref="poster")
    profile_pic = db.Column(db.String(256))


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

#10 Post
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    # ForeignKey - get 'poster'
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
