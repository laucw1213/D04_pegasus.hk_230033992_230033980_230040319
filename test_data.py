from app import db, app
from app.models import User, Post, Category, Product, Order


app_context = app.app_context()
app_context.push()
db.drop_all()
db.create_all()

u1 = User(username='a', email='john@example.com')
u2 = User(username='b', email='susan@example.com')
u1.set_password("a")
u2.set_password("b")
db.session.add(u1)
db.session.add(u2)
u1.follow(u2)
u2.follow(u1)

p1 = Post(body='my first post!', author=u1)
p2 = Post(body='my first post!', author=u2)
db.session.add(p1)
db.session.add(p2)

# Create some categories
category1 = Category(name='CPU')
category2 = Category(name='Display Card')

db.session.add(category1)
db.session.add(category2)

# Create some products
product1 = Product(name='i7', price=100, category=category1)
product2 = Product(name='4090', price=90, category=category2)
product3 = Product(name='4080', price=80, category=category2)

db.session.add(product1)
db.session.add(product2)
db.session.add(product3)

# Create an order
order1 = Order()

# Add some products to the order
order1.add_product(product1)
order1.add_product(product3)

db.session.add(order1)

# Commit the changes to the database

db.session.commit()
