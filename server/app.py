#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
try:
    from flask_migrate import Migrate
except ModuleNotFoundError:
    Migrate = None

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

if Migrate:
    migrate = Migrate(app, db)

db.init_app(app)

# Ensure database tables exist and seed minimal data for tests/dev
with app.app_context():
    db.create_all()
    if not Bakery.query.first():
        b1 = Bakery(name='Delightful donuts')
        b2 = Bakery(name='Incredible crullers')
        db.session.add_all([b1, b2])
        db.session.commit()

        bg1 = BakedGood(name='Chocolate dipped donut', price=2, bakery=b1)
        bg2 = BakedGood(name='Apple-spice filled donut', price=3, bakery=b1)
        bg3 = BakedGood(name='Glazed honey cruller', price=3, bakery=b2)
        bg4 = BakedGood(name='Chocolate cruller', price=3, bakery=b2)

        db.session.add_all([bg1, bg2, bg3, bg4])
        db.session.commit()

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(  bakeries,   200  )

@app.route('/bakeries/<int:id>')
def bakery_by_id(id):

    bakery = Bakery.query.filter_by(id=id).first()
    bakery_serialized = bakery.to_dict()
    return make_response ( bakery_serialized, 200  )

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    return make_response( baked_goods_by_price_serialized, 200  )
   

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()
    return make_response( most_expensive_serialized,   200  )

@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    name = request.form.get('name')
    price = request.form.get('price')
    bakery_id = request.form.get('bakery_id')

    new_bg = BakedGood(name=name, price=price, bakery_id=bakery_id)
    db.session.add(new_bg)
    db.session.commit()

    return make_response(new_bg.to_dict(), 201)

@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    bakery = Bakery.query.get(id)
    if not bakery:
        return make_response({"error": "Bakery not found"}, 404)

    name = request.form.get('name')
    if name:
        bakery.name = name

    db.session.commit()

    return make_response(bakery.to_dict(), 200)

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    bg = BakedGood.query.get(id)
    if not bg:
        return make_response({"error": "Baked good not found"}, 404)

    db.session.delete(bg)
    db.session.commit()

    return make_response({"message": "Baked good deleted"}, 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)