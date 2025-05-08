from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, PasswordField, EmailField, BooleanField, SubmitField, SubmitField, SelectField
from wtforms.validators import DataRequired, length, NumberRange
from flask_wtf.file import FileField, FileRequired


class SignUpForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Tên người dùng', validators=[DataRequired(), length(min=2)])
    password1 = PasswordField('Nhập mật khẩu', validators=[DataRequired(), length(min=6)])
    password2 = PasswordField('Nhập lại mật khẩu', validators=[DataRequired(), length(min=6)])
    submit = SubmitField('Đăng ký')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Nhập mật khẩu', validators=[DataRequired()])
    submit = SubmitField('Đăng nhập')


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Mật khẩu hiện tại', validators=[DataRequired(), length(min=6)])
    new_password = PasswordField('Mật khẩu mới', validators=[DataRequired(), length(min=6)])
    confirm_new_password = PasswordField('Nhập lại mật khẩu mới', validators=[DataRequired(), length(min=6)])
    change_password = SubmitField('Thay đổi mật khẩu')


class ShopItemsForm(FlaskForm):
    product_name = StringField('Tên khóa học', validators=[DataRequired()])
    current_price = FloatField('Giá hiện tại', validators=[DataRequired()])
    previous_price = FloatField('Giá gốc', validators=[DataRequired()])
    # in_stock = IntegerField('In Stock', validators=[DataRequired(), NumberRange(min=0)])
    product_picture = FileField('Ảnh minh họa khóa học', validators=[DataRequired()])
    flash_sale = BooleanField('Flash Sale')

    add_product = SubmitField('Thêm khóa học')
    update_product = SubmitField('Cập nhật')

# khác với đơn hàng vật lý
class OrderForm(FlaskForm):
    order_status = SelectField('Order Status', choices=[
        ('Pending', 'Pending'),           # Chờ xử lý
        ('Payment Received', 'Payment Received'),   # Đã nhận thanh toán
        ('Access Granted', 'Access Granted'),       # Đã cấp quyền truy cập
        ('Completed', 'Completed'),       # Hoàn thành
        ('Canceled', 'Canceled')         # Đã hủy
    ])
    update = SubmitField('Update Status')

