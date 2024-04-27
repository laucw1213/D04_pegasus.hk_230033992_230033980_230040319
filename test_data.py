from app import db, app
from app.models import User, Category, Product, Order


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




# Create some categories
category1 = Category(name='CPU')
category2 = Category(name='Display Card')
category3 = Category(name='RAM')
category4 = Category(name='SSD')
category5 = Category(name='Motherboard')



db.session.add(category1)
db.session.add(category2)
db.session.add(category3)
db.session.add(category4)
db.session.add(category5)

# Create some products
product1 = Product(name='Intel Core i7-14700K 20核心28線程 Tray', price=3249, category=category1, image_path='img/i7.avif')
product2 = Product(name='Intel Core i9-14900KS 24核心32線程 Box', price=5699, category=category1, image_path='img/i9.avif')
product3 = Product(name='ASUS 華碩 DUAL GeForce RTX 4060 Ti EVO 8G OC', price=3599, category=category2, image_path='img/4060.avif')
product4 = Product(name='MSI 微星 VENTUS 3X GeForce RTX 4070 Ti Super 16G GDDR6X OC', price=7199, category=category2, image_path='img/4070.avif')
product5 = Product(name='Team Elite Plus DDR5 5600MHz 32GB (16GB x 2)', price=780, category=category3, image_path='img/TeamElite.avif')
product6 = Product(name='ADATA XPG GAMMIX D20 32GB (16GB x2) DDR4 3200MHz BLACK', price=719, category=category3, image_path='img/ADATA.avif')
product7 = Product(name='Team MP33 PRO 1TB 3D TLC M.2 NVMe PCIe 3.0 x4 SSD', price=469, category=category4, image_path='img/MP33.avif')
product8 = Product(name='Kingston Fury Renegade 2TB 3D TLC M.2 NVMe PCIe 4.0 x 4 SSD', price=1230, category=category4, image_path='img/Kingston.avif')
product9 = Product(name='ASUS 華碩 PRIME H610M-K D4 Micro-ATX 主機板 (DDR4)', price=699, category=category5, image_path='img/ASUS.avif')
product10 = Product(name='MSI 微星 MAG X670E TOMAHAWK WIFI ATX 主機板 (DDR5)', price=2350, category=category5, image_path='img/MSI.avif')

db.session.add(product1)
db.session.add(product2)
db.session.add(product3)
db.session.add(product4)
db.session.add(product5)
db.session.add(product6)
db.session.add(product7)
db.session.add(product8)
db.session.add(product9)
db.session.add(product10)

# Create an order
order1 = Order()

# Add some products to the order
order1.add_product(product1)
order1.add_product(product3)

db.session.add(order1)

# Commit the changes to the database

db.session.commit()
