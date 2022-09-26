from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.dashboard"))
            else:
                flash("Incorrect password!", category="error")
        else:
            flash("Username does not exists!", category="error")
    return render_template("login.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        username = request.form.get("username")
        firstName = request.form.get("firstName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists!", category="error")
        elif len(username) < 3:
            flash("Username must have at least 3 characters!", category="error")
        elif len(firstName) < 3:
            flash("First name must have at least 3 character!", category="error")
        elif password1 != password2:
            flash("Passwords don't match!", category="error")
        elif len(password1) < 5:
            flash("Password must have at least 5 characters!", category="error")
        else:
            new_user = User(
                username=username,
                first_name=firstName,
                password=generate_password_hash(password1, method="sha256"),
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Your account created! You've been logged in.", category="success")
            login_user(new_user, remember=True)
            return redirect(url_for("views.dashboard"))
    return render_template("sign_up.html", user=current_user)


@auth.route("/user", methods=["GET", "POST"])
@login_required
def user():
    if request.method == "POST":
        user = User.query.get(current_user.id)
        firstName = request.form.get("firstName")
        password = request.form.get("currentPassword")
        password1 = request.form.get("newPassword1")
        password2 = request.form.get("newPassword2")
        if check_password_hash(user.password, password):
            if request.form.get("submit_button") == "change":
                if firstName:
                    if len(firstName) < 3:
                        flash(
                            "First name must have at least 3 character!",
                            category="error",
                        )
                    else:
                        user.first_name = firstName
                        flash("First name has been changed!", category="success")
                if password1 and password2:
                    if password1 == password2:
                        user.password = generate_password_hash(
                            password1, method="sha256"
                        )
                        flash("Password has been changed!", category="success")
                    else:
                        flash("Passwords don't match!", category="error")
                db.session.commit()
            elif request.form.get("submit_button") == "delete":
                for etag in user.etags:
                    db.session.delete(etag)
                for itag in user.itags:
                    db.session.delete(itag)
                for expense in user.expenses:
                    db.session.delete(expense)
                for income in user.incomes:
                    db.session.delete(income)
                db.session.delete(user)
                db.session.commit()
                logout_user()
                flash("Account has been deleted", category="success")
                return redirect(url_for("auth.sign_up"))
        else:
            flash("Incorrect password!", category="error")
    return render_template("user.html", user=current_user)
