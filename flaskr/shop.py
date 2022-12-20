
from flask import (Blueprint, flash, g, redirect,
                   render_template, request, session, url_for)
from flaskr.db import get_db

from werkzeug.utils import secure_filename
from flaskr.auth import login_required
bp = Blueprint('shop', __name__, url_prefix='/shop')


@bp.route('/edit-item', methods=('GET', 'POST'))
@login_required
def edit_item():
    db = get_db()
    item = db.execute("SELECT * FROM item WHERE id = ?",
                      (request.cookies.get('id'))).fetchone()
    if request.method == 'POST':
        item_name = request.form['name']
        item_price = request.form['price']
        item_quantity = request.form['quantity']
        error = None

        if not item_name:
            error = "Item name must be specified"
        elif not item_price:
            error = "Item price must be specified"
        elif not item_quantity:
            error = "Item quantity must be specified"
        item_price = float(item_price)
        item_quantity = int(item_quantity)
        if item_price <= 0:
            error = "Item Price must be greater than 0"
        elif item_quantity <= 0:
            error = "Item quantity must be greater then 0"

        db.execute("UPDATE item SET name = ?, price = ?, quantity = ? WHERE id = ?",
                   (item_name, item_price, item_quantity, request.cookies.get('id')))
        db.commit()
        flash(error)
        return redirect(url_for('shop.item_list'))

    if g.user['type'] == 'admin':
        return render_template('shop/admin/edit_item.html', item=item)
    else:
        return render_template('error.html'), {"Refresh": "5; url=/"}


@bp.route('/list', methods=('GET', 'POST'))
@login_required
def item_list():
    db = get_db()
    search = None

    error = None

    if 'delete' in request.args:
        id = request.args['delete']
        exists = db.execute(
            "SELECT * FROM item WHERE id = ?", (id,)).fetchone()
        if exists is not None:
            db.execute("DELETE FROM item WHERE id = ?", (id,))
            db.commit()
    elif 'edit' in request.args:
        exists = db.execute("SELECT * FROM item WHERE id = ?",
                            (request.args['edit'],)).fetchone()
        if exists is not None:
            red = redirect(url_for('shop.edit_item'))
            red.set_cookie('id', request.args['edit'])
            return redirect(url_for('shop.item_list'))
    elif 'search' in request.args:
        searchItem = '%' + request.args['search'].lower() + '%'
        search = db.execute(
            "SELECT * FROM item WHERE (lower(name) LIKE ?) ORDER BY date_created DESC", (searchItem,)).fetchall()
    elif 'buy' in request.args:
        item = db.execute('SELECT * FROM item WHERE id = ?',
                          (request.args['buy'])).fetchone()
        if request.method == "POST":
            quantity = request.form['quantity']
            if not quantity:
                error = "Quantity is required"
            elif int(quantity) <= 0:
                error = "Quantity must be greater than 0"
            elif int(quantity) > item['quantity']:
                error = "Quantity must not be greater then the available stock"
            elif error is None:
                total = int(quantity) * item['price']
                id = db.execute('INSERT INTO receipt(item_id, buyer_id, quantity, total) VALUES (?, ?, ?, ?)',
                           (item['id'], g.user['id'], quantity, total)).lastrowid
                db.execute('UPDATE item SET quantity = ? WHERE id = ?', (item['quantity'] - int(quantity), item['id']))
                db.commit()
                receipt = db.execute(f"SELECT * FROM receipt WHERE id = {id}").fetchone()
                return render_template('shop/receipt.html', receipt=receipt)    
            else:

                flash(error)
        return render_template('shop/buy_item.html', item=item)

    elif 'delete_all' in request.args and g.user['type'] == 'admin':
        db.execute('DELETE FROM item WHERE 1=1')
        db.commit()
    items = (db.execute("SELECT * FROM item ORDER BY date_created DESC").fetchall()
             ) if search is None else search
    if g.user['type'] == 'admin':
        return render_template('shop/admin/item_list.html', items=items)
    else:
        return render_template('shop/item_list.html', items=items)


@bp.route('/add-items', methods=('GET', 'POST'))
@login_required
def add_item():
    if request.method == 'POST':
        item_name = request.form['name']
        item_price = request.form['price']
        item_quantity = request.form['quantity']
        error = None
        db = get_db()

        if not item_name:
            error = "Item name must be specified"
        elif not item_price:
            error = "Item price must be specified"
        elif not item_quantity:
            error = "Item quantity must be specified"
        item_price = float(item_price)
        item_quantity = int(item_quantity)
        if item_price <= 0:
            error = "Item Price must be greater than 0"
        elif item_quantity <= 0:
            error = "Item quantity must be greater then 0"

        if error is None:
            try:
                db.execute("INSERT INTO item(name, price, quantity) VALUES (?, ?, ?)",
                           (item_name, item_price, item_quantity))
                db.commit()
            except db.IntegrityError:
                error = f"Item with name: {item_name} already exists"
            else:
                error = f"Item: {item_name} added successfully"
                return redirect(url_for('shop.add_item'))
        flash(error)
    if g.user['type'] == 'admin':
        return render_template('shop/admin/add-item.html')
    else:
        return render_template('error.html'), {"Refresh": "5; url=/"}
