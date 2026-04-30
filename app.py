from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "secret123"

USERNAME = "admin"
PASSWORD = "1234"

products = [
    {"id": 1, "name": "T-Shirt", "sp": 500, "cp": 300, "quantity": 50, "sales": 20},
    {"id": 2, "name": "Jeans", "sp": 1200, "cp": 800, "quantity": 40, "sales": 10},
    {"id": 3, "name": "Shirt", "sp": 800, "cp": 500, "quantity": 30, "sales": 15},
    {"id": 4, "name": "Jacket", "sp": 2000, "cp": 1500, "quantity": 20, "sales": 5},
    {"id": 5, "name": "Hoodie", "sp": 1500, "cp": 1000, "quantity": 25, "sales": 8},
    {"id": 6, "name": "Sweater", "sp": 1300, "cp": 900, "quantity": 35, "sales": 12},
    {"id": 7, "name": "Kurti", "sp": 900, "cp": 600, "quantity": 50, "sales": 25},
    {"id": 8, "name": "Saree", "sp": 2500, "cp": 1800, "quantity": 15, "sales": 6},
    {"id": 9, "name": "Dress", "sp": 1800, "cp": 1200, "quantity": 18, "sales": 7},
    {"id": 10, "name": "Skirt", "sp": 700, "cp": 400, "quantity": 45, "sales": 20},
    {"id": 11, "name": "Shorts", "sp": 600, "cp": 350, "quantity": 60, "sales": 30},
    {"id": 12, "name": "Blazer", "sp": 3000, "cp": 2200, "quantity": 10, "sales": 4},
    {"id": 13, "name": "Tracksuit", "sp": 2200, "cp": 1600, "quantity": 22, "sales": 9},
    {"id": 14, "name": "Leggings", "sp": 500, "cp": 300, "quantity": 70, "sales": 35},
    {"id": 15, "name": "Palazzo Pants", "sp": 900, "cp": 600, "quantity": 30, "sales": 12},
    {"id": 16, "name": "Denim Jacket", "sp": 2500, "cp": 1800, "quantity": 12, "sales": 5},
    {"id": 17, "name": "Formal Trousers", "sp": 1400, "cp": 1000, "quantity": 28, "sales": 11},
    {"id": 18, "name": "Sweatpants", "sp": 1200, "cp": 800, "quantity": 33, "sales": 14},
    {"id": 19, "name": "Tank Top", "sp": 400, "cp": 200, "quantity": 80, "sales": 40},
    {"id": 20, "name": "Coat", "sp": 3500, "cp": 2500, "quantity": 8, "sales": 3}
]

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['user'] = USERNAME
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    
    total_profit = 0

    for p in products:
        p['profit'] = (p['sp'] - p['cp']) * p['sales']
        p['profit_percent'] = round((p['profit'] / (p['cp'] * p['sales'])) * 100, 2) if p['sales'] > 0 else 0
        total_profit += p['profit']

    return render_template('index.html', products=products, total_profit=total_profit)

@app.route('/add', methods=['POST'])
def add():
    products.append({
        "id": len(products)+1,
        "name": request.form['name'],
        "sp": int(request.form['sp']),
        "cp": int(request.form['cp']),
        "quantity": int(request.form['quantity']),
        "sales": int(request.form['sales'])
    })
    return redirect('/dashboard')

@app.route('/delete/<int:id>')
def delete(id):
    global products
    products = [p for p in products if p['id'] != id]
    return redirect('/dashboard')

@app.route('/edit/<int:id>')
def edit(id):
    product = next(p for p in products if p['id'] == id)
    return render_template('edit.html', p=product)
@app.route('/credit/<int:id>', methods=['POST'])

def credit_note(id):
    if 'user' not in session:
        return redirect('/')
    
    return_qty = int(request.form['return_qty'])
    
    for p in products:
        if p['id'] == id:
            # Stock wapas badha do
            p['quantity'] = int(p['quantity']) + return_qty
            # Sales me se minus kar do
            p['sales'] = int(p['sales']) - return_qty
            if p['sales'] < 0:  # Negative na ho
                p['sales'] = 0
            break
    
    return redirect('/dashboard')

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    for p in products:
        if p['id'] == id:
            p['name'] = request.form['name']
            p['sp'] = int(request.form['sp'])
            p['cp'] = int(request.form['cp'])
            p['quantity'] = int(request.form['quantity'])
            p['sales'] = int(request.form['sales'])
    return redirect('/dashboard')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query'].lower()
    filtered = [p for p in products if query in p['name'].lower()]
    
    total_profit = 0
    for p in filtered:
        p['profit'] = (p['sp'] - p['cp']) * p['sales']
        p['profit_percent'] = round((p['profit'] / (p['cp'] * p['sales'])) * 100, 2) if p['sales'] > 0 else 0
        total_profit += p['profit']

    return render_template('index.html', products=filtered, total_profit=total_profit)
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')
@app.route('/credit/<int:id>', methods=['POST'])
def credit(id):
    return_qty = int(request.form['return_qty'])
    
    # 1. Product dhundo
    product = Product.query.get(id)
    
    if return_qty > product.sales:
        return "Error: Return qty sales se zyada nahi ho sakti", 400
    
    # 2. Stock aur Sales update karo
    product.quantity = product.quantity + return_qty   # Stock wapas aaya
    product.sales = product.sales - return_qty         # Sale kam hui
    
    # 3. Profit wapas calculate karo - Ye line important hai Boss
    product.profit = (product.sp - product.cp) * product.sales
    
    # 4. Profit % wapas calculate karo
    if product.cp * product.sales != 0:
        product.profit_percent = round((product.profit / (product.cp * product.sales)) * 100, 2)
    else:
        product.profit_percent = 0
    
    # 5. DB me save karo
    db.session.commit()
    return redirect('/')

app.run(debug=True)