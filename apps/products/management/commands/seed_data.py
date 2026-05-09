import random
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from apps.accounts.models import User
from apps.products.models import Category, Brand, Product
from apps.sales.models import Sale

TODAY = datetime.date(2026, 4, 26)

CATEGORIES = [
    {'id': 'cat-mobiles',    'name': 'Mobiles',           'icon': '◰', 'color': '#F97316'},
    {'id': 'cat-cases',      'name': 'Cases & Covers',    'icon': '◳', 'color': '#7C3AED'},
    {'id': 'cat-glasses',    'name': 'Screen Guards',     'icon': '◱', 'color': '#0EA5E9'},
    {'id': 'cat-earphones',  'name': 'Earphones',         'icon': '◲', 'color': '#10B981'},
    {'id': 'cat-chargers',   'name': 'Chargers & Cables', 'icon': '◧', 'color': '#EAB308'},
    {'id': 'cat-speakers',   'name': 'Speakers',          'icon': '◨', 'color': '#EC4899'},
    {'id': 'cat-watches',    'name': 'Smart Watches',     'icon': '◩', 'color': '#06B6D4'},
    {'id': 'cat-powerbanks', 'name': 'Power Banks',       'icon': '◪', 'color': '#84CC16'},
]

PRODUCTS_RAW = [
    # id, name, cat, brand, stock, cost, price, color, compat, sold30d, low_thr
    ('p1','Samsung Galaxy A13 (4GB/64GB)','cat-mobiles','Samsung',12,11200,13499,'Black',[],28,5),
    ('p2','Samsung Galaxy A14 5G (6GB/128GB)','cat-mobiles','Samsung',8,14800,17999,'Blue',[],22,5),
    ('p3','Redmi Note 13 (8GB/128GB)','cat-mobiles','Redmi',15,15500,18499,'Black',[],35,5),
    ('p4','Redmi 12C (4GB/64GB)','cat-mobiles','Redmi',4,7200,8999,'Green',[],18,5),
    ('p5','iPhone 13 (128GB)','cat-mobiles','Apple',3,48000,54999,'Black',[],6,4),
    ('p6','Realme Narzo 60 (8GB/128GB)','cat-mobiles','Realme',9,13800,16499,'Green',[],14,5),
    ('p7','Vivo Y27 (6GB/128GB)','cat-mobiles','Vivo',7,14200,16999,'Blue',[],11,5),
    ('p8','Poco X5 (8GB/256GB)','cat-mobiles','Poco',6,17500,20999,'Black',[],13,5),
    ('c1','Soft Silicone Back Cover','cat-cases','Spigen',45,80,249,'Black',['Samsung A13'],62,5),
    ('c2','Soft Silicone Back Cover','cat-cases','Ringke',38,75,229,'Blue',['Samsung A13'],41,5),
    ('c3','Transparent Hard Case','cat-cases','Spigen',52,60,199,'Transparent',['Samsung A13','Samsung A14'],78,5),
    ('c4','Leather Flip Cover','cat-cases','Ringke',12,220,549,'Black',['Samsung A13'],19,5),
    ('c5','Magsafe Case Pro','cat-cases','Spigen',22,320,799,'Black',['iPhone 14','iPhone 15'],24,5),
    ('c6','Camera Protection Case','cat-cases','Spigen',30,110,299,'Pink',['Redmi Note 13'],35,5),
    ('c7','Marble Pattern Back Cover','cat-cases','Ringke',18,95,279,'White',['Samsung A14'],22,5),
    ('c8','Rugged Armor Case','cat-cases','Spigen',14,280,699,'Black',['iPhone 13','iPhone 14'],17,5),
    ('c9','Soft Silicone Back Cover','cat-cases','Spigen',2,80,249,'Red',['Samsung A13'],28,5),
    ('c10','Glitter Case','cat-cases','Ringke',25,100,299,'Pink',['Redmi Note 13','Redmi 12C'],31,5),
    ('g1','Tempered Glass 9H','cat-glasses','Spigen',88,30,149,None,['Samsung A13'],95,5),
    ('g2','Privacy Tempered Glass','cat-glasses','Ringke',24,80,249,None,['iPhone 13','iPhone 14'],18,5),
    ('g3','Edge to Edge Curved Glass','cat-glasses','Spigen',41,60,199,None,['Samsung A14','Samsung S23'],47,5),
    ('g4','Matte Finish Screen Guard','cat-glasses','Ringke',1,45,169,None,['Redmi Note 13'],28,5),
    ('g5','Anti-Blue Light Protector','cat-glasses','Spigen',33,70,219,None,['iPhone 15'],22,5),
    ('e1','Boat Rockerz 235v2','cat-earphones','Boat',42,580,999,'Black',[],88,5),
    ('e2','Boat Airdopes 141','cat-earphones','Boat',35,950,1299,'White',[],72,5),
    ('e3','JBL Tune 130NC','cat-earphones','JBL',11,3200,3999,'Black',[],14,5),
    ('e4','Noise Buds VS104','cat-earphones','Noise',28,980,1499,'Blue',[],51,5),
    ('e5','Mivi Duopods A25','cat-earphones','Mivi',17,750,1199,'White',[],38,5),
    ('e6','Boat Bassheads 100','cat-earphones','Boat',60,280,499,'Black',[],102,5),
    ('ch1','25W Type-C Charger','cat-chargers','Samsung',25,380,699,None,[],58,5),
    ('ch2','20W USB-C Charger','cat-chargers','Apple',14,1200,1799,None,[],22,5),
    ('ch3','USB-C to Lightning Cable 1m','cat-chargers','Apple',18,480,899,None,[],31,5),
    ('ch4','65W Fast Charger SuperVooc','cat-chargers','Realme',8,950,1499,None,[],19,5),
    ('ch5','Micro USB Cable Braided','cat-chargers','Ambrane',65,60,149,None,[],81,5),
    ('s1','Boat Stone 190 Pro','cat-speakers','Boat',9,1100,1599,'Black',[],21,5),
    ('s2','JBL Go 3','cat-speakers','JBL',14,2200,2999,'Red',[],18,5),
    ('s3','Mivi Roam 2','cat-speakers','Mivi',7,1300,1899,'Black',[],12,5),
    ('w1','Noise Colorfit Pro 4','cat-watches','Noise',16,2400,3499,'Black',[],27,5),
    ('w2','Boat Wave Lite','cat-watches','Boat',22,1100,1599,'Silver',[],41,5),
    ('w3','Fire-Boltt Ninja Call Pro','cat-watches','Boat',11,1500,2199,'Black',[],19,5),
    ('pb1','Ambrane 20000mAh PowerLit','cat-powerbanks','Ambrane',18,1100,1699,'Black',[],24,5),
    ('pb2','Mi 10000mAh Pro','cat-powerbanks','Redmi',26,850,1299,'Black',[],38,5),
    ('pb3','Portronics Power Plate 10','cat-powerbanks','Portronics',3,980,1499,'White',[],14,5),
]


class Command(BaseCommand):
    help = 'Seed MongoDB with categories, products, and 30 days of sales'

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true', help='Drop existing data first')

    def handle(self, *args, **options):
        random.seed(42)

        if options['flush']:
            Category.drop_collection()
            Brand.drop_collection()
            Product.drop_collection()
            Sale.drop_collection()
            User.drop_collection()
            self.stdout.write('Collections dropped.')

        # Categories
        for c in CATEGORIES:
            Category.objects(id=c['id']).update_one(
                set__name=c['name'], set__icon=c['icon'], set__color=c['color'], upsert=True
            )
        self.stdout.write(f'  {len(CATEGORIES)} categories seeded.')

        # Brands
        brand_names = list({row[3] for row in PRODUCTS_RAW})
        for name in brand_names:
            Brand.objects(name=name).update_one(set__name=name, upsert=True)
        self.stdout.write(f'  {len(brand_names)} brands seeded.')

        # Products
        for row in PRODUCTS_RAW:
            pid, name, cat, brand, stock, cost, price, color, compat, sold30d, low_thr = row
            Product.objects(id=pid).update_one(
                set__name=name, set__category=cat, set__brand=brand,
                set__stock=stock, set__cost=cost, set__price=price,
                set__color=color, set__compatible_with=compat,
                set__sku=f'ARI-{pid.upper()}', set__sold_30d=sold30d,
                set__rating=round(3.5 + random.random() * 1.5, 2),
                set__added_date='2026-01-15', set__low_stock_threshold=low_thr,
                upsert=True
            )
        self.stdout.write(f'  {len(PRODUCTS_RAW)} products seeded.')

        # Sales (30 days)
        customers = ['Walk-in', 'Rajesh K.', 'Priya S.', 'Amit P.', 'Neha T.', 'Vikram R.']
        methods = ['UPI', 'Cash', 'Card', 'UPI', 'UPI']
        sales_count = 0
        for d in range(29, -1, -1):
            date = (TODAY - datetime.timedelta(days=d)).isoformat()
            num_orders = random.randint(3, 10)
            for i in range(num_orders):
                row = random.choice(PRODUCTS_RAW)
                pid, name, cat, brand, _, cost, price, *_ = row
                qty = random.randint(1, 3)
                sale_id = f'sale-{d}-{i}'
                Sale.objects(id=sale_id).update_one(
                    set__date=date, set__product_id=pid, set__product_name=name,
                    set__category=cat, set__qty=qty,
                    set__revenue=price * qty, set__cost=cost * qty,
                    set__profit=(price - cost) * qty,
                    set__customer=random.choice(customers),
                    set__payment_method=random.choice(methods),
                    upsert=True,
                )
                sales_count += 1
        self.stdout.write(f'  {sales_count} sales seeded.')

        # Default admin user
        if not User.objects(email='admin@arihant.local').first():
            User(
                email='admin@arihant.local',
                password_hash=make_password('admin123'),
                name='Admin',
            ).save()
            self.stdout.write('  Default user: admin@arihant.local / admin123')

        self.stdout.write(self.style.SUCCESS('Seed complete.'))
