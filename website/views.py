from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
from .models import Expense, Income, Itag, Etag, Saving, Note, User
import json
from datetime import datetime


def calculate_expenses(start_date_raw, end_date_raw):
    expenses_data = dict()
    total = 0
    if not start_date_raw or not end_date_raw:
        for etag in current_user.etags:
            sum = 0
            for expense in current_user.expenses:
                if etag.id == expense.tag_id:
                    sum += expense.value
            expenses_data[etag.data] = sum
            total += sum
    else:
        try:
            start_date = datetime.strptime(start_date_raw, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_raw, "%Y-%m-%d")
        except:
            start_date = start_date_raw
            end_date = end_date_raw
        for etag in current_user.etags:
            sum = 0
            for expense in current_user.expenses:
                if (
                    etag.id == expense.tag_id
                    and expense.date <= datetime.date(end_date)
                    and expense.date >= datetime.date(start_date)
                ):
                    sum += expense.value
            expenses_data[etag.data] = sum
            total += sum
    expenses_data_sorted = sorted(expenses_data.items(), key=lambda x: x[1], reverse=True)
    expenses_data = {"Expenses": "Lei"}
    for i in expenses_data_sorted:
        expenses_data[i[0]] = i[1]
    return [expenses_data, total]


def calculate_incomes(start_date_raw, end_date_raw):
    incomes_data = dict()
    total = 0
    if not start_date_raw or not end_date_raw:
        for itag in current_user.itags:
            sum = 0
            for income in current_user.incomes:
                if itag.id == income.tag_id:
                    sum += income.value
            incomes_data[itag.data] = sum
            total += sum
    else:
        try:
            start_date = datetime.strptime(start_date_raw, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_raw, "%Y-%m-%d")
        except:
            start_date = start_date_raw
            end_date = end_date_raw
        for itag in current_user.itags:
            sum = 0
            for income in current_user.incomes:
                if (
                    itag.id == income.tag_id
                    and income.date <= datetime.date(end_date)
                    and income.date >= datetime.date(start_date)
                ):
                    sum += income.value
            incomes_data[itag.data] = sum
            total += sum
    incomes_data_sorted = sorted(incomes_data.items(), key=lambda x: x[1], reverse=True)
    incomes_data = {"Incomes": "Lei"}
    for i in incomes_data_sorted:
        incomes_data[i[0]] = i[1]
    return [incomes_data, total]


def calculate_savings(goal_string):
    savings_data = {"Savings progress": "Lei"}
    if not goal_string:
        if not current_user.savings_goal:
            sum = 0
            for saving in current_user.savings:
                sum += saving.value
            savings_data["Savings"] = sum
        else:
            sum = 0
            for saving in current_user.savings:
                sum += saving.value
            savings_data["Savings"] = sum
            savings_data["Still needing"] = current_user.savings_goal - sum
    else:
        try:
            goal = float(goal_string)
            user = User.query.get(current_user.id)
            user.savings_goal = goal
            db.session.commit()
            sum = 0
            for saving in current_user.savings:
                sum += saving.value
            savings_data["Savings"] = sum
            if goal <= sum:
                goal = sum
            savings_data["Still needing"] = goal - sum
        except:
            flash("Please enter a valid number as goal!", category="error")
    return savings_data


views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
@login_required
def dashboard():
    tabs = [True, False, False]

    note = request.form.get("note")
    goal_string = request.form.get("goal")

    if request.method == "POST":
        if request.form.get("filter_button") == "1":
            pass
        elif request.form.get("filter_button") == "2":
            tabs = [False, True, False]
        elif request.form.get("filter_button") == "3":
            tabs = [False, False, True]
    if tabs[0] == True:
        start_date_raw = request.form.get("start_date_expenses")
        end_date_raw = request.form.get("end_date_expenses")
    elif tabs[1] == True:
        start_date_raw = request.form.get("start_date_incomes")
        end_date_raw = request.form.get("end_date_incomes")
    elif tabs[2] == True:
        start_date_raw = request.form.get("start_date_incomes")
        end_date_raw = request.form.get("end_date_incomes")
    
    [incomes_data, incomes_data_total] = calculate_incomes(start_date_raw, end_date_raw)
    [expenses_data, expenses_data_total] = calculate_expenses(start_date_raw, end_date_raw)
    savings_data = calculate_savings(goal_string)

    if note:
        new_note = Note(data=note, user_id=current_user.id)
        db.session.add(new_note)
        db.session.commit()
        flash("A note has been added!", category="success")

    return render_template(
        "dashboard.html",
        user=current_user,
        tabs=tabs,
        start_date=start_date_raw,
        end_date=end_date_raw,
        goal=goal_string,
        expenses_data=expenses_data,
        incomes_data=incomes_data,
        expenses_data_total=expenses_data_total,
        incomes_data_total=incomes_data_total,
        savings_data=savings_data
    )


@views.route("/delete-note", methods=["POST"])
def delete_note():
    note = json.loads(request.data)
    noteId = note["noteId"]
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            flash("A note has been removed!", category="success")
    return jsonify({})


@views.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses():
    if request.method == "POST":
        value_string = request.form.get("value")
        try:
            value = float(value_string)
        except:
            flash("Please enter a positive valid number as value!", category="error")
            return render_template("expenses.html", user=current_user)
        tag = request.form.get("tag")
        for etag in current_user.etags:
            if etag.data == tag:
                tag_id = etag.id
        date = request.form.get("date")
        date = datetime.strptime(date, "%Y-%m-%d")

        if value <= 0:
            flash("Please enter a positive valid number as value!", category="error")
        else:
            new_expense = Expense(
                value=value, tag_id=tag_id, date=date, user_id=current_user.id
            )
            db.session.add(new_expense)
            db.session.commit()
            flash("An expense entry has been added!", category="success")
    return render_template("expenses.html", user=current_user)


@views.route("/delete-expense", methods=["POST"])
def delete_expense():
    expense = json.loads(request.data)
    expenseId = expense["expenseId"]
    expense = Expense.query.get(expenseId)
    if expense:
        if expense.user_id == current_user.id:
            db.session.delete(expense)
            db.session.commit()
            flash("An expense entry has been removed!", category="success")
    return jsonify({})


@views.route("/incomes", methods=["GET", "POST"])
@login_required
def incomes():
    if request.method == "POST":
        value_string = request.form.get("value")
        try:
            value = float(value_string)
        except:
            flash("Please enter a positive valid number as value", category="error")
            return render_template("incomes.html", user=current_user)
        tag = request.form.get("tag")
        for itag in current_user.itags:
            if itag.data == tag:
                tag_id = itag.id
        date = request.form.get("date")
        date = datetime.strptime(date, "%Y-%m-%d")

        if value <= 0:
            flash("Please enter a positive valid number as value", category="error")
        else:
            new_income = Income(
                value=value, tag_id=tag_id, date=date, user_id=current_user.id
            )
            db.session.add(new_income)
            db.session.commit()
            flash("An income entry has been added!", category="success")
    return render_template("incomes.html", user=current_user)


@views.route("/delete-income", methods=["POST"])
def delete_income():
    income = json.loads(request.data)
    incomeId = income["incomeId"]
    income = Income.query.get(incomeId)
    if income:
        if income.user_id == current_user.id:
            db.session.delete(income)
            db.session.commit()
            flash("An income entry has been removed!", category="success")
    return jsonify({})


@views.route("/etags", methods=["GET", "POST"])
@login_required
def etags():
    if request.method == "POST":
        data = request.form.get("data")
        if len(data) < 1:
            flash("Please enter a tag name!", category="error")
        else:
            unique_tag = True
            for etag in current_user.etags:
                if etag.data == data:
                    flash("Tag name already exists!", category="error")
                    unique_tag = False
        if unique_tag:
            new_etag = Etag(data=data, user_id=current_user.id)
            db.session.add(new_etag)
            db.session.commit()
            flash("A tag has been added!", category="success")
    return render_template("etags.html", user=current_user)


@views.route("/delete-etag", methods=["POST"])
def delete_etag():
    etag = json.loads(request.data)
    etagId = etag["etagId"]
    etag = Etag.query.get(etagId)
    user = User.query.get(current_user.id)
    if etag:
        if etag.user_id == current_user.id:
            for expense in user.expenses:
                if expense.tag_id == etag.id:
                    db.session.delete(expense)
            db.session.delete(etag)
            db.session.commit()
            flash(
                "The tag and all expenses associated have been removed!",
                category="success",
            )
    return jsonify({})


@views.route("/itags", methods=["GET", "POST"])
@login_required
def itags():
    if request.method == "POST":
        data = request.form.get("data")
        if len(data) < 1:
            flash("Please enter a tag name!", category="error")
        else:
            unique_tag = True
            for itag in current_user.itags:
                if itag.data == data:
                    flash("Tag name already exists!", category="error")
                    unique_tag = False
        if unique_tag:
            new_itag = Itag(data=data, user_id=current_user.id)
            db.session.add(new_itag)
            db.session.commit()
            flash("A tag has been added!", category="success")
    return render_template("itags.html", user=current_user)


@views.route("/delete-itag", methods=["POST"])
def delete_itag():
    itag = json.loads(request.data)
    itagId = itag["itagId"]
    itag = Itag.query.get(itagId)
    user = User.query.get(current_user.id)
    if itag:
        if itag.user_id == current_user.id:
            for income in user.incomes:
                if income.tag_id == itag.id:
                    db.session.delete(income)
            db.session.delete(itag)
            db.session.commit()
            flash(
                "The tag and all incomes associated have been removed!",
                category="success",
            )
    return jsonify({})


@views.route("/savings", methods=["GET", "POST"])
@login_required
def savings():
    if request.method == "POST":
        value_string = request.form.get("value")
        try:
            value = float(value_string)
        except:
            flash("Please enter a valid number as value", category="error")
            return render_template("savings.html", user=current_user)
        date = request.form.get("date")
        date = datetime.strptime(date, "%Y-%m-%d")
        if value == 0:
            flash("Please enter a valid number as value", category="error")
        else:
            new_saving = Saving(value=value, date=date, user_id=current_user.id)
            db.session.add(new_saving)
            db.session.commit()
            flash("A saving entry has been added!", category="success")
    return render_template("savings.html", user=current_user)


@views.route("/delete-saving", methods=["POST"])
def delete_saving():
    saving = json.loads(request.data)
    savingId = saving["savingId"]
    saving = Saving.query.get(savingId)
    if saving:
        if saving.user_id == current_user.id:
            db.session.delete(saving)
            db.session.commit()
            flash("A saving entry has been removed!", category="success")
    return jsonify({})
