from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
from .models import Expense, Income, Itag, Etag, Saving, Note, User
import json
from datetime import datetime


def calculate_overview(date_11_raw, date_12_raw):
    data_1 = dict()
    if not date_11_raw or not date_12_raw:
        sum_expenses = 0
        for expense in current_user.expenses:
            sum_expenses += expense.value
        sum_savings = 0
        for saving in current_user.savings:
            sum_savings += saving.value
        sum_incomes = 0
        for income in current_user.incomes:
            sum_incomes += income.value
        diff = sum_incomes - sum_expenses - sum_savings
        if diff < 0:
            data_1["Over the budget"] = -diff
        else:
            data_1["Expenses"] = sum_expenses
            if sum_savings > 0:
                data_1["Savings"] = sum_savings
            data_1["Leftovers"] = diff
    else:
        try:
            date_11 = datetime.strptime(date_11_raw, "%Y-%m-%d")
            date_12 = datetime.strptime(date_12_raw, "%Y-%m-%d")
            date_11 = datetime.date(date_11)
            date_12 = datetime.date(date_12)
        except:
            date_11 = datetime.date(date_11_raw)
            date_12 = datetime.date(date_12_raw)
        sum_expenses = 0
        for expense in current_user.expenses:
            if expense.date >= date_11 and expense.date <= date_12:
                sum_expenses += expense.value
        sum_savings = 0
        for saving in current_user.savings:
            if saving.date >= date_11 and saving.date <= date_12:
                sum_savings += saving.value
        sum_incomes = 0
        for income in current_user.incomes:
            if income.date >= date_11 and income.date <= date_12:
                sum_incomes += income.value
        diff = sum_incomes - sum_expenses - sum_savings
        if diff < 0:
            data_1["Over the budget"] = -diff
        else:
            data_1["Leftovers"] = diff
            data_1["Expenses"] = sum_expenses
            if sum_savings > 0:
                data_1["Savings"] = sum_savings
    data_1_sorted = sorted(data_1.items(), key=lambda x: x[1], reverse=True)
    data_1 = {"Expense": "Lei"}
    for i in data_1_sorted:
        data_1[i[0]] = i[1]
    return data_1


def calculate_expenses(date_21_raw, date_22_raw):
    data_2 = dict()
    total = 0
    if not date_21_raw or not date_22_raw:
        for etag in current_user.etags:
            sum = 0
            for expense in current_user.expenses:
                if etag.id == expense.tag_id:
                    sum += expense.value
            data_2[etag.data] = sum
            total += sum
    else:
        try:
            date_21 = datetime.strptime(date_21_raw, "%Y-%m-%d")
            date_22 = datetime.strptime(date_22_raw, "%Y-%m-%d")
        except:
            date_21 = date_21_raw
            date_22 = date_22_raw
        for etag in current_user.etags:
            sum = 0
            for expense in current_user.expenses:
                if (
                    etag.id == expense.tag_id
                    and expense.date <= datetime.date(date_22)
                    and expense.date >= datetime.date(date_21)
                ):
                    sum += expense.value
            data_2[etag.data] = sum
            total += sum
    data_2_sorted = sorted(data_2.items(), key=lambda x: x[1], reverse=True)
    data_2 = {"Expense": "Lei"}
    for i in data_2_sorted:
        data_2[i[0]] = i[1]
    return [data_2, total]


def calculate_savings(goal_string):
    data_3 = {"Savings progress": "Lei"}
    if not goal_string:
        if not current_user.savings_goal:
            sum = 0
            for saving in current_user.savings:
                sum += saving.value
            data_3["Savings"] = sum
        else:
            sum = 0
            for saving in current_user.savings:
                sum += saving.value
            data_3["Savings"] = sum
            data_3["Still needing"] = current_user.savings_goal - sum
    else:
        try:
            goal = float(goal_string)
            user = User.query.get(current_user.id)
            user.savings_goal = goal
            db.session.commit()
            sum = 0
            for saving in current_user.savings:
                sum += saving.value
            data_3["Savings"] = sum
            if goal <= sum:
                goal = sum
            data_3["Still needing"] = goal - sum
        except:
            flash("Please enter a valid number as goal!", category="error")
    return data_3


views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
@login_required
def dashboard():
    tab_1 = True
    tab_2 = False
    tab_3 = False

    date_11_raw = request.form.get("date_11")
    date_12_raw = request.form.get("date_12")
    date_21_raw = request.form.get("date_21")
    date_22_raw = request.form.get("date_22")
    note = request.form.get("note")
    goal_string = request.form.get("goal")

    print(date_21_raw)

    if request.method == "POST":
        if request.form.get("submit_button") == "1":
            pass
        elif request.form.get("submit_button") == "2":
            tab_2 = True
        elif request.form.get("submit_button") == "3":
            tab_3 = True

    data_1 = calculate_overview(date_11_raw, date_12_raw)
    [data_2, data_2_total] = calculate_expenses(date_21_raw, date_22_raw)
    data_3 = calculate_savings(goal_string)

    if note:
        new_note = Note(data=note, user_id=current_user.id)
        db.session.add(new_note)
        db.session.commit()
        flash("A note has been added!", category="success")

    return render_template(
        "dashboard.html",
        user=current_user,
        data_3=data_3,
        tab_1=tab_1,
        tab_2=tab_2,
        tab_3=tab_3,
        date_11=date_11_raw,
        date_12=date_12_raw,
        date_21=date_21_raw,
        date_22=date_22_raw,
        goal=goal_string,
        data_1=data_1,
        data_2=data_2,
        data_2_total=data_2_total,
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
