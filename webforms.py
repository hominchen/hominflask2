from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea

# ==== FlaskForm ====
class NamerForm(FlaskForm):
    name = StringField("請問你的名子？", validators=[DataRequired()])
    submit = SubmitField("確認")

class UserForm(FlaskForm):
    name = StringField("姓名", validators=[DataRequired()])
    username = StringField("暱稱")  
    email = StringField("信箱", validators=[DataRequired()])
    favorite_color = StringField("喜愛的顏色")
    password_hash = PasswordField('請輸入密碼', 
        validators=[DataRequired(), 
        EqualTo('password_hash2', message='密碼必須匹配')])
    # 驗證的密碼並不會被儲存到資料庫，用一個變量來承接
    password_hash2 = PasswordField('請再次輸入密碼', validators=[DataRequired()])
    submit = SubmitField("確認")

#08 Hash相符測試
class PasswordForm(FlaskForm):  
    email = StringField("你的信箱?", validators=[DataRequired()])
    password_hash = PasswordField("你的密碼?", validators=[DataRequired()])
    submit = SubmitField("確認")

#10 Post
class PostForm(FlaskForm):
    title = StringField("標題", validators=[DataRequired()])
    content = StringField("內容", validators=[DataRequired()], widget=TextArea())
    author = StringField("作者", validators=[DataRequired()])
    slug = StringField("文號", validators=[DataRequired()])
    submit = SubmitField("確認")

#11 Login登入
class LoginForm(FlaskForm):
    email = StringField("信箱", validators=[DataRequired()])
    password = PasswordField("密碼", validators=[DataRequired()])
    submit = SubmitField("Submit")
