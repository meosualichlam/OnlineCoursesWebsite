from flask import Blueprint, render_template, flash, send_from_directory, redirect
from flask_login import login_required
from flask_login import current_user
from .forms import ShopItemsForm, OrderForm
from werkzeug.utils import secure_filename
from .models import Product, Order, Customer
from . import db

admin = Blueprint('admin',__name__)

@admin.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('../media', filename)

@admin.route('/add-shop-items', methods=['GET', 'POST'])
@login_required
def add_shop_items():
    if current_user.id == 1:
        form = ShopItemsForm()
        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            flash_sale = form.flash_sale.data
            description = form.description.data  # Lấy mô tả khóa học
            video_url = form.video.data  # Lấy video học thử
            duration = form.duration.data  # Lấy thời gian khóa học

            file = form.product_picture.data
            file_name = secure_filename(file.filename) #sẽ thay đổi tên file sao cho hợp lệ
            file_path = f'./media/{file_name}'
            file.save(file_path)
        #     new product
            new_shop_item = Product()
            new_shop_item.product_name = product_name
            new_shop_item.current_price = current_price
            new_shop_item.previous_price = previous_price
            new_shop_item.flash_sale = flash_sale
            new_shop_item.product_picture = file_path
            new_shop_item.description = description  # Lấy mô tả từ form
            new_shop_item.duration = duration  # Lấy thời gian từ form
            new_shop_item.video_url = video_url  # Lấy video từ form

            try:
                db.session.add(new_shop_item)
                db.session.commit()
                flash(f'{product_name} đã được thêm thành công!')
                print('Khóa học được thêm')
                return render_template('add-shop-items.html',form=form)
                # return redirect('/shop-items')
            except Exception as e:
                print(e)
                flash('Khóa học chưa được thêm')
        return render_template('add-shop-items.html', form=form)

    return render_template('404.html')
@admin.route('/shop-items', methods=['GET', 'POST'])
@login_required
def shop_items():
    if current_user.id == 1:
        items = Product.query.order_by(Product.date_added).all()
        return render_template('shop_items.html', items=items)
    return render_template('404.html')

# update
@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    if current_user.id == 1:
        form = ShopItemsForm()

        # Lấy sản phẩm cần cập nhật
        item_to_update = Product.query.get(item_id)

        if not item_to_update:
            flash('Sản phẩm không tồn tại!')
            return redirect('/shop-items')

        # Điền các giá trị hiện tại vào form
        form.product_name.data = item_to_update.product_name
        form.previous_price.data = item_to_update.previous_price
        form.current_price.data = item_to_update.current_price
        form.flash_sale.data = item_to_update.flash_sale
        form.description.data = item_to_update.description
        form.duration.data = item_to_update.duration
        form.video.data = item_to_update.video_url

        if form.validate_on_submit():
            # Lấy các giá trị từ form
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            flash_sale = form.flash_sale.data
            description = form.description.data
            video_url = form.video.data
            duration = form.duration.data

            file = form.product_picture.data

            # Kiểm tra nếu có hình ảnh mới được tải lên
            if file:
                file_name = secure_filename(file.filename)
                file_path = f'./media/{file_name}'
                file.save(file_path)
            else:
                file_path = item_to_update.product_picture
            try:
                # Cập nhật thông tin trong bảng Product
                product_update = Product.query.filter_by(id=item_id).first()
                product_update.product_name = product_name
                product_update.current_price = current_price
                product_update.previous_price = previous_price
                product_update.flash_sale = flash_sale
                product_update.product_picture = file_path
                product_update.description = description  # Cập nhật mô tả
                product_update.duration = duration  # Cập nhật thời gian
                product_update.video_url = video_url  # Cập nhật video
                # Lưu thay đổi vào cơ sở dữ liệu
                db.session.commit()
                flash(f'{product_name} cập nhật thành công!', 'success')
                print('Khóa học được cập nhật thành công')
                return redirect('/shop-items')
            except Exception as e:
                print('Khóa học không được cập nhật', e)
                flash(f'Khóa học {product_name} chưa được cập nhật!!!', 'error')
        return render_template('update_item.html', form=form, item=item_to_update)

    return render_template('404.html')


# delete
@admin.route('/delete-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    if current_user.id == 1:
        try:
            item_to_delete = Product.query.get(item_id)
            db.session.delete(item_to_delete)
            db.session.commit()
            flash('Một khóa học đã bị xóa')
            return redirect('/shop-items')
        except Exception as e:
            print('Khóa học chưa bị xóa', e)
            flash('Khóa học chưa bị xóa!!')
        return redirect('/shop-items')

    return render_template('404.html')


@admin.route('/view-orders')
@login_required
def order_view():
    if current_user.id == 1:
        orders = Order.query.all()
        return render_template('view_orders.html', orders=orders)
    return render_template('404.html')

@admin.route('/update-order/<int:order_id>', methods=['GET','POST'])
@login_required
def update_user(order_id):
    if current_user.id==1:
        form = OrderForm()

        order = Order.query.get(order_id)

        if form.validate_on_submit():
            status = form.order_status.data
            order.status = status

            try:
                db.session.commit()
                flash(f'Khóa học {order_id} được cập nhật thành công.')
                return redirect('/view-orders')
            except Exception as e:
                print(e)
                flash(f'Khóa học {order_id} chưa được cập nhật.')
                return redirect('/view-orders')

        return render_template('order_update.html', form=form)
    return render_template('404.html')

@admin.route('/customers')
@login_required
def display_customer():
    if current_user.id == 1:
        customers = Customer.query.all()
        return render_template('customers.html', customers=customers)
    return render_template('404.html')

@admin.route('/admin-page')
@login_required
def admin_page():
    if current_user.id == 1:
        return render_template('admin.html')
    return render_template('404.html')
