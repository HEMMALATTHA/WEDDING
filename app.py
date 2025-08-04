from flask import Flask, render_template, session, jsonify, request, redirect, url_for, flash

from flask_session import Session
import re
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = 'supersecret'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


# Dummy database
users= {}

@app.route('/faq')
def faq():
    return render_template("faq.html")

@app.route('/howtoorder')
def howtoorder():
    return render_template("howtoorder.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/about')
def about():
    return render_template("about.html")
@app.route('/cards')
def cards():
    return render_template("cards.html")


cards_data = [
    {"id": 1, "title": "The blue Wedding Cards", "price": 72.25, "image": "images/blue.png"},
    {"id": 2, "title": "Ganesha Wedding Cards", "price": 25.25, "image": "images/ganesh.png"},
    {"id": 3, "title": "Wedding Cards Favour Box", "price": 39.45, "image": "images/favour.png"},
    {"id": 4, "title": "Theme Wedding Cards", "price": 30.00, "image": "images/theme.png"},
    {"id": 5, "title": "Elegant Peacock Wedding Cards", "price": 15.00, "image": "images/peacock.png"},
    {"id": 6, "title": "Royal Scroll Wedding Cards", "price": 75.00, "image": "images/royal.png"},
    {"id": 7, "title": "Vintage Wedding Cards", "price": 30.15, "image": "images/vintage.png"},
    {"id": 8, "title": "Editable Wedding Cards", "price": 35.55, "image": "images/editable.png"},
    {"id": 9, "title": "Traditional Wedding Cards", "price": 25.00, "image": "images/trad.png"},
    {"id": 10, "title": "Gate Fold Wedding Cards", "price": 43.20, "image": "images/gate.png"},
    {"id": 11, "title": "Unique Wedding Cards", "price": 22.50, "image": "images/unique.png"},
    {"id": 12, "title": "Wardrobe Wedding Cards", "price": 59.75, "image": "images/ward.png"}
]

@app.route('/hindu')
def hindu():
    wishlist = session.get('wishlist', [])
    return render_template('hindu.html', cards=cards_data, wishlist=wishlist)

@app.route('/wishlist')
def wishlist():
    wishlist = session.get('wishlist', [])
    filtered = [c for c in cards_data if c["id"] in wishlist]
    return render_template('wishlist.html', cards=filtered)

@app.route('/toggle-wishlist/<int:card_id>', methods=['POST'])
def toggle_wishlist(card_id):
    wishlist = session.get('wishlist', [])
    if card_id in wishlist:
        wishlist.remove(card_id)
        in_wishlist = False
    else:
        wishlist.append(card_id)
        in_wishlist = True
    session['wishlist'] = wishlist
    return jsonify(success=True, in_wishlist=in_wishlist)


@app.route('/search')
def search():
    popular_cards = [
        {'image': 'cards/theme.png', 'title': 'Post Theme Wedding Card'},
        {'image': 'cards/gold.png', 'title': 'Scroll Wedding Card'},
        {'image': 'cards/redwhite.png', 'title': 'Theme Wedding Card'},
        {'image': 'cards/muslim.jpg', 'title': 'Customize Wedding Card'},
        {'image': 'cards/laser.png', 'title': 'Laser Wedding Card'},
        {'image': 'cards/red.jpg', 'title': 'Hindu Wedding Card'},
    ]

    ideas_cards = [
        {'image': 'cards/royall.jpg', 'title': 'Hindu wedding Card'},
        {'image': 'cards/simple.png', 'title': 'Simple wedding Card'},
        {'image': 'cards/muslim.png', 'title': 'Muslim wedding Card'},
        {'image': 'cards/royal.png', 'title': 'Scroll wedding Card'},
        {'image': 'cards/exclusive.png', 'title': 'Luxury wedding Card'},
    ]

    return render_template("search.html", popular_cards=popular_cards, ideas_cards=ideas_cards)


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        if 'signup' in request.form:
            email = request.form['signup_email']
            password = request.form['signup_password']
            repassword = request.form['signup_repassword']

            # Form validations
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash("Invalid email format.", "danger")
            elif password != repassword:
                flash("Passwords do not match.", "danger")
            elif email in users:
                flash("User already exists.", "warning")
            else:
                users[email] = password
                flash("Sign up successful! You can now login.", "success")
                return redirect(url_for('auth', show_login='true'))

        elif 'login' in request.form:
            email = request.form['login_email']
            password = request.form['login_password']

            if users.get(email) == password:
                session['user'] = email
                flash("Login successful.", "success")
                return redirect(url_for('home'))
            else:
                flash("Invalid login credentials.", "danger")

    return render_template('auth.html')



@app.route('/')
def home():
    if 'user' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('auth'))
    return render_template('home.html', user=session['user'])
@app.route('/buy/<int:card_id>')
def buy(card_id):
    card = next((c for c in cards_data if c['id'] == card_id), None)
    if not card:
        return "Card not found", 404
    related = [c for c in cards_data if c['id'] != card_id][:7]
    return render_template('buy.html', card=card, related=related)



@app.context_processor
def inject_datetime():
    return {'datetime': datetime}
@app.route('/ordersummary', methods=['POST'])
def ordersummary():
    data = request.form

    now = datetime.now()
    product = {
        'title': data['product'],
        'price': float(data['price']),
        'qty': int(data['qty']),
        'compliment': data['compliment'],
        'image': data['image'],
        'date': now.strftime('%d %b'),
        'time': now.strftime('%I.%M%p').lower(),
        'coupon': 'MAR0057'
    }
    return render_template('ordersum.html', product=product)


@app.route('/orderconfirm', methods=['GET', 'POST'])
def orderconfirm():
    if request.method == 'POST':
        # Get actual order data from form or session
        product = request.form.get("product", "The Blue Wedding Card")
        image = request.form.get("image", "images/blue.png")
        price = float(request.form.get("price", 153.0))
        qty = int(request.form.get("qty", 2))
    else:
        # Dummy data for GET testing
        product = "The Blue Wedding Card"
        image = "images/blue.png"
        price = 153.0
        qty = 2

    subtotal = price * qty
    tax_rate = 0.18
    tax = round(subtotal * tax_rate, 2)
    discount = 5.00
    total = round(subtotal + tax - discount, 2)

    order = {
        "order_id": random.randint(1000000000, 9999999999),
        "sku_code": "KSN0054",
        "sn_code": "SN 54",
        "product_title": product,
        "product_image": image,
        "price": price,
        "qty": qty,
        "email": "jhon057@gmail.com",
        "name": "Jhon",
        "address": "123 Elm street\nAnytown, ABC 12345\nAnywhere.",
        "subtotal": subtotal,
        "shipping": 0.00,
        "tax_rate": tax_rate,
        "discount": discount,
        "tax": tax,
        "total": total
    }

    return render_template("orderconfirm.html", order=order)



if __name__ == "__main__":
    app.run(debug=True)
