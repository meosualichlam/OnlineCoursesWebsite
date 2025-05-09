from flask import Blueprint, render_template, flash, redirect, request, jsonify
from .models import Product, Cart, Order
from flask_login import login_required, current_user
from . import db
from intasend import APIService

API_PUBLISHABLE_KEY = 'ISPubKey_test_d32402bd-a96c-4c4e-8b9f-033d62e41ae0'

API_TOKEN = 'ISSecretKey_test_887ede72-ec20-4758-a77f-4bb48ec8947e'

views = Blueprint('views',__name__)

@views.route('/')
def home():
    items = Product.query.filter_by(flash_sale=True).all()  # Thêm .all() để lấy tất cả các sản phẩm
    return render_template('home.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])


@views.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    item_to_add = Product.query.get(item_id)

    # Kiểm tra nếu sản phẩm đã có trong giỏ hàng
    item_exists = Cart.query.filter_by(product_link=item_id, customer_link=current_user.id).first()

    # Nếu sản phẩm đã có trong giỏ hàng, không làm gì thêm
    if item_exists:
        flash(f'{item_exists.product.product_name} đã có sẵn trong giỏ hàng.')
        return redirect(request.referrer)

    # Nếu sản phẩm chưa có trong giỏ hàng, tạo mục mới với quantity = 1
    new_cart_item = Cart()
    new_cart_item.quantity = 1  # Quantity cố định là 1
    new_cart_item.product_link = item_to_add.id
    new_cart_item.customer_link = current_user.id

    try:
        db.session.add(new_cart_item)
        db.session.commit()
        flash(f'{new_cart_item.product.product_name} đã được thêm vào giỏ hàng.')
    except Exception as e:
        print('Khóa học không được thêm vào giỏ hàng', e)
        flash(f'Không thể thêm khóa học {new_cart_item.product.product_name} vào giỏ hàng của bạn.')

    return redirect(request.referrer)

@views.route('/cart')
@login_required
def show_cart():
    # Lấy tất cả các sản phẩm trong giỏ hàng của người dùng
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    # Tính tổng số tiền giỏ hàng
    amount = 0
    for item in cart:
        amount += item.product.current_price  # Sản phẩm chỉ có 1 đơn vị, không cần nhân với quantity
    # Thêm phí vận chuyển (giả sử là 20k)
    total = amount

    return render_template('cart.html', cart=cart, amount=amount, total=total)


@views.route('removecart')
@login_required
def remove_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        db.session.delete(cart_item)
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price
        data = {
            'amount': amount,
            'total': amount
        }

        return jsonify(data)


@views.route('/place-order')
@login_required
def place_order():
    customer_cart = Cart.query.filter_by(customer_link=current_user.id)
    if customer_cart:
        try:
            total = 0
            for item in customer_cart:
                total += item.product.current_price

            service = APIService(token=API_TOKEN, publishable_key=API_PUBLISHABLE_KEY, test=True)
            create_order_response = service.collect.mpesa_stk_push(phone_number='254712345678', email='linhtrb0412@gmail.com',
                                                                   amount=total, narrative='Purchase of goods')

            for item in customer_cart:
                new_order = Order()
                new_order.price = item.product.current_price
                new_order.status = create_order_response['invoice']['state'].capitalize()
                new_order.payment_id = create_order_response['id']

                new_order.product_link = item.product_link
                new_order.customer_link = item.customer_link

                db.session.add(new_order)

                product = Product.query.get(item.product_link)

                db.session.delete(item)

                db.session.commit()

            flash('Mua khóa học thành công')
            return redirect('/orders')
        except Exception as e:
            print(e)
            flash('Mua khoá học không thành công.')
            return redirect('/')
    else:
        flash('Giỏ hàng của bạn trống.')
        return redirect('/')


@views.route('/orders')
@login_required
def order():
    orders = Order.query.filter_by(customer_link=current_user.id).all()
    return render_template('orders.html', orders=orders)


@views.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
        return render_template('search.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])
    # same với cart
    return render_template('search.html')

@views.route('/course-detail/<int:item_id>')
def course_detail(item_id):
    # Lấy sản phẩm từ cơ sở dữ liệu
    item = Product.query.get(item_id)

    # Kiểm tra xem sản phẩm có tồn tại không
    if item:
        # Lấy các thông tin từ sản phẩm
        description = item.description
        duration = item.duration
        video_url = item.video_url
        return render_template('course_detail.html', item=item, description=description, duration=duration, video_url=video_url)
    else:
        flash('Khóa học không tồn tại!')
        return redirect('/')

@views.route('/all-courses')
def all_courses():
    # Lấy tham số lọc và sắp xếp từ query string
    price_filter = request.args.get('price')
    sort = request.args.get('sort')

    query = Product.query

    # Lọc theo giá
    if price_filter == 'lt50':
        query = query.filter(Product.current_price < 50000)
    elif price_filter == '50-100':
        query = query.filter(Product.current_price >= 50000, Product.current_price <= 100000)
    elif price_filter == '100-200':
        query = query.filter(Product.current_price > 100000, Product.current_price <= 200000)
    elif price_filter == 'gt200':
        query = query.filter(Product.current_price > 200000)

    # Sắp xếp
    if sort == 'newest':
        query = query.order_by(Product.date_added.desc())
    elif sort == 'asc':
        query = query.order_by(Product.current_price.asc())
    elif sort == 'desc':
        query = query.order_by(Product.current_price.desc())

    courses = query.all()
    return render_template('all_courses.html', courses=courses,
                           cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])

@views.route('/chatbot', methods=['POST'])
def chatbot():
    # Lấy tin nhắn từ người dùng
    data = request.get_json()
    user_message = data.get('message', '').lower()

    # Logic phản hồi nâng cấp với nhiều trường hợp
    if any(keyword in user_message for keyword in ['chào', 'xin chào', 'halo', 'hello']):
        reply = "Xin chào! Rất vui được trò chuyện với bạn. Bạn cần giúp gì hôm nay?"
    elif any(keyword in user_message for keyword in ['khóa học', 'khoa hoc', 'course', 'hoc']):
        reply = "Chúng tôi có rất nhiều khóa học hấp dẫn! Bạn có thể xem danh sách khóa học ở trang chủ (/) hoặc tại /all-courses. Bạn quan tâm đến khóa học nào? Nếu cần, hãy hỏi thêm về chi tiết!"
    elif any(keyword in user_message for keyword in ['giá', 'gia', 'price', 'bao nhiêu', 'chi phí']):
        reply = "Bạn có thể lọc khóa học theo giá ở thanh điều hướng trên cùng. Các mức giá bao gồm: dưới 50.000 VNĐ, 50.000 - 100.000 VNĐ, 100.000 - 200.000 VNĐ, và trên 200.000 VNĐ. Bạn muốn tìm khóa học trong khoảng giá nào? Hoặc hỏi cụ thể giá của khóa học nào đó!"
    elif any(keyword in user_message for keyword in ['hỗ trợ', 'ho tro', 'help', 'giúp', 'support']):
        reply = "Tôi sẵn sàng hỗ trợ bạn! Bạn có thể hỏi về khóa học, giá cả, cách mua hàng, hoặc bất kỳ vấn đề nào. Hãy cho tôi biết bạn cần gì nhé!"
    elif any(keyword in user_message for keyword in ['mua', 'mua hàng', 'thanh toán', 'payment']):
        reply = "Để mua khóa học, hãy thêm khóa học vào giỏ hàng (sử dụng nút 'Thêm giỏ hàng') và chọn 'Place Order' để thanh toán qua M-Pesa. Nếu cần hỗ trợ thanh toán, hãy cho tôi biết!"
    elif any(keyword in user_message for keyword in ['liên hệ', 'contact', 'email', 'phone']):
        reply = "Bạn có thể liên hệ với chúng tôi qua email: linhtrb0412@gmail.com hoặc gọi số hỗ trợ (giả định: 0909 123 456). Hãy cho tôi biết nếu bạn cần thêm thông tin!"
    elif any(keyword in user_message for keyword in ['Cảm ơn', 'thanks', 'yêu bạn', 'đẹp']):
        reply = "Tôi cũng yêu bạn. Hãy cho tôi biết nếu bạn cần thêm thông tin!"
    else:
        reply = "Xin lỗi, tôi chưa hiểu ý bạn. Bạn có thể nói rõ hơn không? Dưới đây là một số gợi ý: hỏi về khóa học, giá cả, cách mua hàng, hỗ trợ, hoặc chào hỏi!"

    # Trả về phản hồi dưới dạng JSON
    return jsonify({'reply': reply})
