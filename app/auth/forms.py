from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired("邮箱不能为空"), Length(1, 64), Email("无效的邮箱地址")])
    password = PasswordField('密码', validators=[DataRequired("密码不能为空"), Length(6, 16, "密码长度范围在6~16之间")])
    remember_me = BooleanField("保持登录状态")
    submit = SubmitField("登录")


class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired("邮箱不能为空"), Length(1, 64), Email("无效的邮箱地址")])
    username = StringField('用户名', validators=[DataRequired("用户名不能为空"), Length(3, 20, '用户名3到20个字符之间'),
                                              Regexp('^[\u4e00-\u9fa5_a-zA-Z0-9]+$', 0,
                                                     '用户名至少包含一个字母、数字或下划线')])
    password = PasswordField('密码', validators=[DataRequired("密码不能为空"), Length(6, 16, "密码长度范围在6~16之间"), EqualTo('password2', message='密码不匹配')])
    password2 = PasswordField('确认密码', validators=[DataRequired("密码不能为空")])
    submit = SubmitField('注册')

    def validate_email(self, filed):
        if User.query.filter_by(email=filed.data).first():
            raise ValidationError("邮箱已注册")

    def valid_username(self, filed):
        if User.query.filter_by(username=filed.data).first():
            raise ValidationError("用户名已被使用")

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[
        DataRequired(), Length(6, 16, "密码长度范围在6~16之间"), EqualTo('password2', message='密码不匹配')])
    password2 = PasswordField('确认密码',
                              validators=[DataRequired()])
    submit = SubmitField('更新')

class PasswordResetRequestForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('重置密码')


class PasswordResetForm(FlaskForm):
    password = PasswordField('新密码', validators=[
        DataRequired(), Length(6, 16, "密码长度范围在6~16之间"), EqualTo('password2', message='密码不匹配')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('确认重置')

class ChangeEmailForm(FlaskForm):
    email = StringField('新的邮箱地址', validators=[DataRequired("邮箱不能为空"), Length(1, 64),
                                                 Email("无效的邮箱地址")])
    password = PasswordField('Password', validators=[DataRequired("密码不能为空"), Length(6, 16, "密码长度范围在6~16之间")])
    submit = SubmitField('确认')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被使用')
