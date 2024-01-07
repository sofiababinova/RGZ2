from flask import Blueprint, request, render_template, redirect 
from Db import db
from Db.models import users, profile
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, current_user, logout_user
from sqlalchemy import or_, and_
from sqlalchemy.orm import defer
from sqlalchemy import cast
from sqlalchemy import Integer

rgz1 = Blueprint ("rgz1", __name__)


@rgz1.route('/rgz1/')
def rgz():
    visibleuser = 'Anon'

    return render_template('str1.html', username_form=visibleuser)


@rgz1.route("/rgz1/register", methods=["GET", "POST"])
def register():
    errors = ''

    if request.method == "GET":
        return render_template("register.html", errors=errors)
    
    username_form = request.form.get("username")
    password_form = request.form.get("password")

    if not (username_form or password_form):
        errors = "Пожалуйста, заполните все поля"
        return render_template('register.html', errors=errors)
    
    if len(password_form) < 5:
        errors = "Пароль должен содержать не менее 5 символов"
        return render_template('register.html', errors=errors)

    isUserExist = users.query.filter_by (username=username_form).first()
    
    if isUserExist is not None:
        errors = "Пользователь с данным именем уже существует"
        return render_template ("register.html", errors=errors)


    hashedPswd = generate_password_hash(password_form, method='pbkdf2')
    newUser = users(username=username_form, password=hashedPswd)

    db.session.add(newUser)
    db.session.commit()

    return redirect ("/rgz1/login")


@rgz1.route("/rgz1/login", methods=["GET", "POST"])
def login():
    errors = ''

    if request.method == "GET":
        return render_template ("login.html")

    username_form = request.form.get("username")
    password_form = request.form.get("password")

    if not (username_form or password_form):
        errors = "Пожалуйста, заполните все поля"
        return render_template('login.html', errors=errors)

    my_user = users.query.filter_by(username=username_form).first()

    if my_user is None:
        errors = "Пользователь не существует"
        return render_template('login.html', errors=errors)

    if not check_password_hash(my_user.password, password_form):
        errors = "Неправильный пароль"
        return render_template('login.html', errors=errors)

    if my_user is not None:
        if check_password_hash(my_user.password, password_form):
            login_user(my_user, remember=False)
            return render_template ("str1.html", username_form=username_form)
        
    return render_template ("login.html")


@rgz1.route("/rgz1/logout")
@login_required
def logout():
    logout_user()
    return redirect("/rgz1/")


@rgz1.route('/rgz1/new_profile', methods=["GET", "POST"])
@login_required
def registerprofile():

    errors = ''

    if request.method == "GET":
        return render_template("new_profile.html", errors=errors)

    if request.method == "POST":
        type_of_service = request.form.get("type_of_service")
        experience = request.form.get("experience")
        price = request.form.get("price")
        about_me = request.form.get("about_me")

        if len(type_of_service) == 0:
                errors = "Заполните поле вид услуги, которую вы предоставляете!"
                return render_template("new_profile.html", errors=errors)
        
        if len(experience) == 0:
                errors = "Заполните поле стаж!"
                return render_template("new_profile.html", errors=errors)
        
        if len(price) == 0:
                errors = "Заполните поле цена услуги!"
                return render_template("new_profile.html", errors=errors)

        new_profile = profile(type_of_service=type_of_service, experience=experience, price=price, about_me=about_me, user_id=current_user.id)
        
        db.session.add(new_profile)
        db.session.commit()
        
        return redirect("/rgz1/profile")
    
    return render_template ("/rgz1/profile")


@rgz1.route('/rgz1/profile', methods=["GET", "POST"])
@login_required
def Profile():
    my_profile = profile.query.filter_by(user_id=current_user.id).all()

    type_of_service = my_profile[0].type_of_service
    experience = my_profile[0].experience
    price = my_profile[0].price
    about_me = my_profile[0].about_me

    return render_template('profile.html', type_of_service=type_of_service, experience=experience, price=price, about_me=about_me)

@rgz1.route('/rgz1/edit', methods=["POST"])
@login_required
def edit():

    print(current_user.id)

    if request.method == "POST":
        type_of_service = request.form.get("type_of_service")
        experience = request.form.get("experience")
        price = request.form.get("price")
        about_me = request.form.get("about_me")


    my_profile = profile.query.filter_by(user_id=current_user.id).all()

    
    if my_profile:
        my_profile[0].type_of_service = type_of_service
        my_profile[0].experience = experience
        my_profile[0].price = price
        my_profile[0].about_me = about_me
        db.session.commit()
        return render_template('profile.html', type_of_service=type_of_service, experience=experience, price=price, about_me=about_me)
    
    db.session.commit()

    return redirect('/rgz1/profile')


@rgz1.route('/rgz1/delete', methods=["POST"])
@login_required
def delete():
    
    user = current_user

    profile.query.filter_by(user_id=user.id).delete()


    db.session.delete(user)
    db.session.commit()
    logout_user()

    return redirect('/rgz1/')

@rgz1.route('/rgz1/search', methods=["GET", "POST"])
def search():
    if request.method == "POST":
        # Получить параметры поиска из формы
        type_of_service = request.form.get('type_of_service')
        experience_from = request.form.get('experience_from', type=int)
        experience_to = request.form.get('experience_to', type=int)
        price_from = request.form.get('price_from', type=float)
        price_to = request.form.get('price_to', type=float)

        # Построение условий поиска
        conditions = []
        if type_of_service:
            conditions.append(profile.type_of_service == type_of_service)
        if experience_from is not None:
            conditions.append(cast(profile.experience, Integer) >= experience_from)
        if experience_to is not None:
            conditions.append(cast(profile.experience, Integer) <= experience_to)
        if price_from is not None:
            conditions.append(profile.price >= price_from)
        if price_to is not None:
            conditions.append(profile.price <= price_to)

        # Выполнение запроса в базе данных
        profiles = profile.query.filter(and_(*conditions)).options(defer(profile.type_of_service), defer(profile.experience), defer(profile.price)).all()

        return render_template('search.html', profiles=profiles)

    # Если метод GET, вернуть пустую страницу для отображения формы поиска
    return render_template('search.html')