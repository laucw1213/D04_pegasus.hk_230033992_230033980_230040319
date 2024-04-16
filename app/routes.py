from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g
from flask import session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from flask_babel import _, get_locale
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, \
    ResetPasswordRequestForm, ResetPasswordForm, OrderForm
from app.models import User, Post, Product, Order, Category, Cart, CartItem, OrderItem
from app.email import send_password_reset_email


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'index', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'index', page=posts.prev_num) if posts.prev_num else None
    cart = Cart(user_id=current_user.id)
    db.session.add(cart)
    db.session.commit()

    # 將購物車的 ID 保存到 session 中
    session['cart_id'] = cart.id
    return render_template('index.html.j2', title=_('Home'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'explore', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'explore', page=posts.prev_num) if posts.prev_num else None
    return render_template('index.html.j2', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html.j2', title=_('Sign In'), form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html.j2', title=_('Register'), form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
            _('Check your email for the instructions to reset your password'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html.j2',
                           title=_('Reset Password'), form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if user is None:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html.j2', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.followed_posts().paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'index', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'index', page=posts.prev_num) if posts.prev_num else None
    return render_template('user.html.j2', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html.j2', title=_('Edit Profile'),
                           form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('user', username=username))

@app.route('/order_form', methods=['GET', 'POST'])
def order_form():
    form = OrderForm()
    query = request.args.get('query')  # 從請求參數中獲取查詢字串
    categories = Category.query.all()
    products = Product.query.all()  # Define products here

    if request.method == 'POST':
        category_id = request.form.get('category')
        if category_id:
            products = Product.query.filter_by(category_id=category_id).all()  # filter products by category

    if query:
        products = Product.query.filter(Product.name.contains(query)).all()  # 如果有查詢字串，則查詢名稱包含該字串的所有產品

    # 獲取當前用戶的購物車
    cart = Cart.query.get(session['cart_id'])

    if cart is None:
        # 如果 cart 為 None，則重定向到首頁
        return redirect(url_for('index'))

    # 獲取購物車中的產品信息
    cart_items = [(item.product, item.quantity) for item in cart.items]

    # 計算購物車中的總價
    total_price = sum([item.product.price * item.quantity for item in cart.items])

    # 計算購物車中的總數量
    quantity_total = sum([item.quantity for item in cart.items])

    # 計算總金額
    grand_total = total_price

    # 計算總金額加上運費
    shipping_cost = 100  # 請根據您的運費策略設定這個值
    grand_total_plus_shipping = grand_total + shipping_cost

    return render_template('order_form.html.j2', title='Order Form', form=form, products=products, categories=categories, cart_items=cart_items, total_price=total_price, quantity_total=quantity_total, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping)


@app.route('/order_info', methods=['GET', 'POST'])
@login_required
def order_info():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    order = orders[0] if orders else None
    return render_template('order_info.html.j2', orders=orders, order=order)



@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    # 從表單數據中獲取產品 ID
    product_id = request.form.get('product_id')

    # 獲取當前用戶的購物車
    cart_id = session.get('cart_id')
    if cart_id is None:
        # 如果 cart_id 為 None，則創建一個新的購物車
        cart = Cart()
        db.session.add(cart)
        db.session.commit()
        session['cart_id'] = cart.id
    else:
        cart = Cart.query.get_or_404(cart_id)

    # 從數據庫中獲取產品
    product = Product.query.get_or_404(product_id)

    # 創建一個新的 CartItem 並將其添加到購物車中
    cart_item = CartItem(product=product, quantity=1)
    cart.items.append(cart_item)

    # 將變更保存到數據庫中
    db.session.commit()

    # 重定向回 order_form 頁面
    return redirect(url_for('order_form'))

@app.route('/view_cart')
def view_cart():
    # 獲取當前用戶的購物車
    cart = Cart.query.get(session['cart_id'])

    if cart is None:
        # 如果 cart 為 None，則重定向到首頁
        return redirect(url_for('index'))

    # 獲取購物車中的產品信息
    cart_items = [(item.product, item.quantity) for item in cart.items]

    # 計算購物車中的總價
    total_price = sum([item.product.price * item.quantity for item in cart.items])

    # 計算購物車中的總數量
    quantity_total = sum([item.quantity for item in cart.items])

    # 計算總金額
    grand_total = total_price

    # 計算總金額加上運費
    shipping_cost = 100  # 請根據您的運費策略設定這個值
    grand_total_plus_shipping = grand_total + shipping_cost

    return render_template('view_cart.html.j2', cart_items=cart_items, total_price=total_price, quantity_total=quantity_total, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping)

@app.route('/remove-from-cart/<int:product_id>')
def remove_from_cart(product_id):
    # 從數據庫中獲取產品
    product = Product.query.get_or_404(product_id)

    # 獲取當前用戶的購物車
    cart = Cart.query.get_or_404(session['cart_id'])

    # 從購物車中移除產品
    cart.products.remove(product)

    # 將變更保存到數據庫中
    db.session.commit()

    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # 獲取當前用戶的購物車
    cart = Cart.query.get(session['cart_id'])

    if cart is None:
        # 如果 cart 為 None，則重定向到首頁
        return redirect(url_for('index'))

    # 獲取購物車中的產品信息
    cart_items = [(item.product, item.quantity) for item in cart.items]

    # 計算購物車中的總價
    total_price = sum([item.product.price * item.quantity for item in cart.items])

    # 計算購物車中的總數量
    quantity_total = sum([item.quantity for item in cart.items])

    # 計算總金額
    grand_total = total_price

    # 計算總金額加上運費
    shipping_cost = 100  # 請根據您的運費策略設定這個值
    grand_total_plus_shipping = grand_total + shipping_cost

    if request.method == 'POST':
        # 在這裡處理結帳邏輯，例如清空購物車、創建訂單等

        # 創建一個新的訂單
        order = Order(user=current_user, total=grand_total_plus_shipping)
        db.session.add(order)

        # 將購物車中的每個項目添加到訂單中
        for item in cart.items:
            order_item = OrderItem(order=order, product=item.product, quantity=item.quantity)
            db.session.add(order_item)

        # 清空購物車
        for item in cart.items:
            db.session.delete(item)

        # 提交變更到數據庫
        db.session.commit()

        # 結帳完成後，重定向到一個新的頁面，例如訂單確認頁面
        return redirect(url_for('order_confirmation', order_id=order.id))
    return render_template('checkout.html.j2', cart=cart, total_price=total_price, quantity_total=quantity_total, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping)

@app.route('/order_confirmation/<int:order_id>', methods=['GET'])
@login_required
def order_confirmation(order_id):
    order = Order.query.get(order_id)
    if order is None or order.user_id != current_user.id:
        abort(404)
    return render_template('order_confirmation.html.j2', order=order)