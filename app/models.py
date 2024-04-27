
from datetime import datetime, timedelta, timezone
from hashlib import md5
from app import app, db, login
import jwt

from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.orm import relationship

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({"reset_password": self.id,
                           "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)},
                          app.config["SECRET_KEY"], algorithm="HS256")

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")[
                "reset_password"]
        except:           
            return None
        return User.query.get(id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

orders_products = db.Table('orders_products',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)

carts_products = db.Table('carts_products',
    db.Column('cart_id', db.Integer, db.ForeignKey('cart.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)

cart_products = db.Table('cart_products',
    db.Column('cart_id', db.Integer, db.ForeignKey('cart.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('quantity', db.Integer)  # 新增一個 quantity 列來儲存每個產品的數量
)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    product = db.relationship('Product', backref='cart_items')

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    items = db.relationship('CartItem', backref='cart', lazy='dynamic')

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    products = db.relationship('Product', backref='category', lazy='dynamic')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    price = db.Column(db.Float)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    image_path = db.Column(db.String(128))  # 新增的圖片路徑欄位
    

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship('Product')

    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total = db.Column(db.Float)

    # 建立與 User 類別的關聯
    user = relationship('User', backref='orders')

    # 建立與 OrderItem 類別的關聯
    items = db.relationship('OrderItem', backref='order', lazy='dynamic')

    def add_product(self, product):
        order_item = OrderItem(product=product, order=self)
        self.items.append(order_item)
        db.session.commit()
