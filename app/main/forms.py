from flask_wtf import FlaskForm
from flask_wtf.html5 import URLField, EmailField
from flask_pagedown.fields import PageDownField
from wtforms import TextAreaField, SubmitField, StringField, BooleanField, SelectField, ValidationError, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Email, Regexp
from ..models import Role, User, Category, Comment


class EditProfileForm(FlaskForm):
    about_me = TextAreaField('About me')
    submit = SubmitField("提交")


class EditProfileAdminForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('用户名', validators=[DataRequired("用户名不能为空"), Length(3, 20, '用户名3到20个字符之间'),
                                              Regexp('^[\u4e00-\u9fa5_a-zA-Z0-9]+$', 0,
                                                     '用户名至少包含一个字母、数字或下划线')])
    confirmed = BooleanField('激活邮箱')
    role = SelectField('角色', coerce=int)
    about_me = TextAreaField("关于我")
    submit = SubmitField("提交")

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def valid_email(self, filed):
        if filed.data != self.user.email and User.query.filter_by(email=filed.data).first():
            raise ValidationError("邮箱已被注册")

    def valid_username(self, filed):
        if filed.data != self.user.username and User.query.filter_by(username=filed.data).first():
            raise ValidationError("用户名已被使用")


class PostForm(FlaskForm):
    title = StringField("标题", validators=[DataRequired()])
    category = SelectField("分类", validators=[DataRequired()], coerce=int)
    summary = TextAreaField("摘要", validators=[DataRequired()])
    body = PageDownField("内容", validators=[DataRequired()])
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name) for category
            in Category.query.order_by(Category.name).all()]

class CommentForm(FlaskForm):
    name = StringField('姓名', validators=[DataRequired()])
    email = EmailField('邮箱', validators=[Email()])
    url = URLField('网址', validators=[DataRequired()])
    body = TextAreaField('内容', validators=[DataRequired()])
    replay_id = IntegerField(default=None)
    submit = SubmitField('提交')

    def validate_website(self, field):
        if field.data[:4] != "http" and field.data[:5] != "https":
            raise ValidationError("请输入正确网址")

    def validate_replay_id(self, field):
        if field.data:
            if Comment.query.get(field.data) is None:
                raise ValidationError("回复出错")





