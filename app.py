from flask import Flask, render_template, request
from link_log_st import link_st, log_st

from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from db import SessionLocal
from schemas import CreateProduct
from models import *
app = Flask(__name__)

@app.teardown_appcontext
def shutdown_session(exception=None):
    print('Session is closed')
    SessionLocal.remove()

@app.route('/', methods=['GET'])
def hello_world():
    link_st.__init__()
    link_st.home = 'active'
    context = {
        'title': 'Главная',
        'pagename': 'Булочная - Теплый Хлеб',
        'logged': log_st.is_logged_in,
        'LinkStatus': link_st,
    }
    return render_template('home.html', **context)


@app.route("/products", methods=['GET', 'POST'])
def get_products(db=SessionLocal, create_product = CreateProduct):
    search = request.args.get('search')
    link_st.__init__()
    link_st.products = 'active'
    if search is None:
        products = db.scalars(select(Product)).all()
        search = ''
    else:
        products = db.scalars(select(Product).where(Product.name.icontains(search.lower()))).all()

    context = {
        'title': 'Продукты',
        'pagename': 'Продукты',
        'logged': log_st.is_logged_in,
        'LinkStatus': link_st,
        'products': products,
        'is_logged_in': log_st.is_logged_in,
        'search': search,
    }
    if request.method == 'POST':
        product = db.scalar(select(Product).where(Product.name == create_product.name))
        if product is None:
            db.execute(insert(Product).values(name=create_product.name,
                                              weight=create_product.weight,
                                              price=create_product.price,
                                              image_url=create_product.image_url,
                                              ))
            db.commit()
            return {'status_code': 'HTTP_201_CREATED',
                    'add_product': 'Successful'}
        else:
            return {'status_code': 'HTTP_400_BAD_REQUEST',
                    'detail': 'Product already exists'}
    return render_template("products.html", **context)


@app.route("/products/add_to_cart", methods=['POST'])
def add_product_to_cart(db=SessionLocal):
    form = request.form
    try:
        product = db.query(Product).filter(Product.name == form.get('card_button')).first()
        user = db.query(User).filter(User.email == log_st.email).first()

        product.user.append(user)
        user.product.append(product)
        db.commit()
    except Exception as e:
        print(e)

    finally:
        products = db.scalars(select(Product)).all()
        context = {
            'title': 'Продукты',
            'pagename': 'Продукты',
            'logged': log_st.is_logged_in,
            'LinkStatus': link_st,
            'products': products,
            'is_logged_in': log_st.is_logged_in,
        }
        return render_template("products.html", **context)


@app.route("/about", methods=['GET'])
def get_about():
    link_st.__init__()
    link_st.about = 'active'
    context = {
        'title': 'Информация',
        'pagename': 'Информация',
        'logged': log_st.is_logged_in,
        'LinkStatus': link_st,
    }
    return render_template("about.html", **context)


@app.route("/log_in", methods=['GET', 'POST'])
def get_log_in(db=SessionLocal):
    if request.method == 'POST':
        form = request.form
        email = form.get('email')
        password = form.get('password')
        if db.scalar(select(User).where(User.email == email)) and password == db.scalar(
                select(User).where(User.email == email)).password:
            link_st.__init__()
            link_st.home = 'active'
            log_st.log_in(email)
            context = {
                'title': 'Главная',
                'pagename': 'Булочная - Теплый Хлеб',
                'logged': log_st.is_logged_in,
                'LinkStatus': link_st,
            }
            return render_template("home.html", **context)

    link_st.__init__()
    link_st.log_in = 'active'
    context = {
        'title': 'Войти',
        'pagename': 'Войти',
        'logged': False,
        'LinkStatus': link_st,
        'error': '',
    }
    return render_template("log_in.html", **context)


@app.route("/sign_up", methods=['GET', 'POST'])
def get_sign_up(db=SessionLocal):
    if request.method == 'POST':
        form = request.form
        email = form.get('email')
        first_name = form.get('first_name')
        last_name = form.get('last_name')
        password = form.get('password')
        password_repeat = form.get('password_repeat')

        def fill_inputs(eml, firstname, lastname, psw, psw_repeat):
            context['email'] = eml
            context['first_name'] = firstname
            context['last_name'] = lastname
            context['password'] = psw
            context['repeat_password'] = psw_repeat

        context = {
            'title': 'Регистрация',
            'pagename': 'Регистрация',
            'logged': False,
            'LinkStatus': link_st
        }

        if password != password_repeat:
            context['error'] = 'Пароли не совпадают'
            fill_inputs(email, first_name, last_name, password, password_repeat)
        else:
            try:
                db.execute(insert(User).values(email=email, first_name=first_name, last_name=last_name, password=password))
                db.commit()
                link_st.__init__()
                link_st.home = 'active'
                log_st.log_in()
                context = {
                    'title': 'Главная',
                    'pagename': 'Булочная - Теплый Хлеб',
                    'logged': log_st.is_logged_in,
                    'LinkStatus': link_st,
                }
                return render_template("home.html", **context)
            except IntegrityError:
                context['error'] = 'Пользователь с таким email уже существует'
                fill_inputs(email, first_name, last_name, password, password_repeat)

        return render_template("sign_up.html", **context)

    link_st.__init__()
    link_st.sign_up = 'active'
    context = {
        'title': 'Регистрация',
        'pagename': 'Регистрация',
        'logged': False,
        'LinkStatus': link_st,
        'error': ''
    }
    return render_template("sign_up.html", **context)



@app.route("/profile/info", methods=['GET', 'POST'])
def get_info(db=SessionLocal):
    # update user data
    if request.method == 'POST':
        form = request.form
        email = form.get('email')
        first_name = form.get('first_name')
        last_name = form.get('last_name')
        # update user data in db.sqlite3
        db.execute(update(User).where(User.email == log_st.email).values(email=email,
                                                                         first_name=first_name,
                                                                         last_name=last_name))
        db.commit()

    # getting all information and transmit them to the page template
    link_st.__init__()
    link_st.profile_info = 'active'
    context = {
        'title': 'Профиль',
        'pagename': 'Профиль',
        'logged': True,
        'LinkStatus': link_st,
        'email': db.scalar(select(User).where(User.email == log_st.email)).email,
        'first_name': db.scalar(select(User).where(User.email == log_st.email)).first_name,
        'last_name': db.scalar(select(User).where(User.email == log_st.email)).last_name,
    }
    return render_template("profile_info.html", **context)


# get '/profile/cart'
@app.route("/profile/cart", methods=['GET'])
def get_cart(db=SessionLocal):
    # get all products selected by the user
    products = db.query(Product).join(Product.user).filter(User.email == log_st.email).all()
    # Another solution: db.query(Product).join(User.product).where(User.email == log_st.email).all()

    link_st.__init__()
    link_st.cart = 'active'
    context = {
        'request': request,
        'title': 'Корзина',
        'pagename': 'Корзина',
        'logged': True,
        'LinkStatus': link_st,
        'total_price': 0,
        'products': '',
    }
    # count total price
    if products:
        context['products'] = products
        for product in products:
            context['total_price'] += product.price

    return render_template("cart.html", **context)


# remove all products (buy all products)
@app.post("/profile/cart/buy")
def buy_products(db=SessionLocal):
    # get current user in database
    user = db.query(User).filter(User.email == log_st.email).first()
    # clear all relationship with Product_table
    user.product.clear()
    db.commit()
    context = {
        'request': request,
        'title': 'Корзина',
        'pagename': 'Корзина',
        'logged': True,
        'LinkStatus': link_st,
        'total_price': 0,
        'products': '',
    }
    return render_template("cart.html", **context)


# remove one product from cart
@app.route("/profile/cart/remove_product", methods=['POST'])
def remove_product(db=SessionLocal):
    # get selected product and current user
    form = request.form
    user = db.query(User).filter(User.email == log_st.email).first()
    product_ = db.query(Product).filter(Product.name == form.get('card_button')).first()

    # removing the product from current user
    user.product.remove(product_)
    db.add(user)
    db.commit()

    context = {
        'request': request,
        'title': 'Корзина',
        'pagename': 'Корзина',
        'logged': True,
        'LinkStatus': link_st,
        'total_price': 0,
        'products': ''
    }
    # update/count total price
    products = db.scalars(select(Product).join(User.product).where(User.email == log_st.email)).all()
    if products:
        context['products'] = products
        for product in products:
            context['total_price'] += product.price
    return render_template("cart.html", **context)


# log out
@app.route("/profile/log_out", methods=['GET'])
def get_log_out():
    link_st.__init__()
    link_st.home = 'active'
    log_st.log_out()
    context = {
        'request': request,
        'title': 'Главная',
        'pagename': 'Булочная - Теплый Хлеб',
        'logged': log_st.is_logged_in,
        'LinkStatus': link_st,
    }
    return render_template("home.html", **context)


if __name__ == '__main__':
    app.run()
