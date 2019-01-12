from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from wtforms import TextAreaField, SubmitField, StringField, BooleanField, SelectField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp
from ..models import Role, User


class EditProfileForm(FlaskForm):
    about_me = TextAreaField('About me')
    submit = SubmitField("提交")


class EditProfileAdminForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('用户名', validators=[DataRequired("用户名不能为空"), Length(3, 20, '用户名3到20个字符之间'),
                                              Regexp('^[\u4e00-\u9fa5_a-zA-Z0-9]+$', 0,
                                                     '用户名至少包含一个字母、数字或下划线')])
    confirmed = BooleanField('激活邮箱')
    role = SelectField('Role', coerce=int)
    about_me = TextAreaField("About me")
    submit = SubmitField("Submit")

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
    body = PageDownField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('提交')

class CommentForm(FlaskForm):
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField('提交')

