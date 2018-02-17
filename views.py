from app import app
from database import db_session
from flask import render_template, redirect, url_for, flash, request
from models import *
from forms import *
from sqlalchemy import exists, desc, and_, func
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import io
import csv
import json
from datetime import date, timedelta, datetime

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

colour_array = ['rgb(99,166,159)',
                'rgb(242,255,172)',
                'rgb(242,131,201)',
                'rgb(242,116,0)',
                'rgb(0,57,58)',
                'rgb(0,138,49)',
                'rgb(255,181,56)',
                'rgb(253,83,35)'
                ]


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('view_accounts'))
    else:
        return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('view_accounts'))
            else:
                error = 'Incorrect password'
        else:
            error = 'User not found'

        return render_template('login.html', form=form, error=error)

    if current_user.is_authenticated:
        return redirect(url_for('view_accounts'))
    else:
        return render_template('login.html', form=form, error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    error = None
    if form.validate_on_submit():
        if db_session.query(exists().where(User.username == form.username.data)).scalar():
            error = 'Username already taken, try again'
            return render_template('signup.html', form=form, error=error)
        elif db_session.query(exists().where(User.email == form.email.data)).scalar():
            error = 'Email is already in use'
            return render_template('signup.html', form=form, error=error)
        else:
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = User(id=None, username=form.username.data, email=form.email.data, password=hashed_password)
            db_session.add(new_user)
            db_session.commit()

            return redirect(url_for('login'))
    if current_user.is_authenticated:
        return redirect(url_for('view_accounts'))
    else:
        return render_template('signup.html', form=form, error=error)


def load_category_chart(start_date, end_date, user_id):

    result = db_session.\
        query(TransactionCategory.name, func.sum(Transaction.amount*-1)).\
        filter(and_(Transaction.date >= start_date, Transaction.date <= end_date, Transaction.user_id == user_id)).\
        join(Transaction.category).\
        group_by(TransactionCategory.name).\
        order_by(func.sum(Transaction.amount*-1).desc())

    data = []
    labels = []
    chart_colours = []
    i = 0
    for datapoint in result:
        labels.append(str(datapoint[0]))
        data.append(float(datapoint[1]))
        chart_colours.append(str(colour_array[i]))
        i += 1

    category_chart_data = [data, chart_colours, labels]

    print(category_chart_data)
    return category_chart_data


@app.route('/dashboard')
@login_required
def dashboard():

    start_date = datetime.strptime('2018/01/01', '%Y/%m/%d')
    end_date = datetime.strptime('2018/01/31', '%Y/%m/%d')

    category_chart_data = load_category_chart(start_date, end_date, current_user.id)

    return render_template('dashboard.html', category_chart_data=category_chart_data)


@app.route('/view_accounts/all')
@login_required
def view_accounts():
    user_accounts = current_user.accounts.all()
    all_uploads = current_user.uploads.all()
    all_transactions = db_session.query(Transaction).\
        filter_by(user_id=current_user.id).\
        order_by(Transaction.date.desc(), Transaction.id.asc())

    unique_categories = []
    for transaction in all_transactions:
        if transaction.category.name not in unique_categories:
            unique_categories.append(transaction.category.name)

    account_choices = []
    for account_type in db_session.query(AccountType):
        account_choices.append((account_type.id, account_type.name))
    add_account_form = AddAccountForm()
    add_account_form.type_id.choices = account_choices
    remove_account_form = RemoveAccountForm()
    upload_form = UploadForm()
    return render_template('accounts.html', accounts=user_accounts, displayed_account=None, uploads=all_uploads,
                           transactions=all_transactions, unique_categories=unique_categories,
                           add_account_form=add_account_form, remove_account_form=remove_account_form,
                           upload_form=upload_form)


@app.route('/view_accounts/<int:account_id>')
@login_required
def view_account(account_id):
    user_accounts = current_user.accounts.all()
    account_ids = [a.id for a in user_accounts]
    if account_id in account_ids:
        account_to_display = user_accounts[account_ids.index(account_id)]
        displayed_account_uploads = account_to_display.uploads.all()
        displayed_account_transactions = db_session.query(Transaction).\
            filter_by(account_id=account_to_display.id).\
            order_by(Transaction.date.desc(), Transaction.id.asc())

        unique_categories = []
        for dispayed_account_transaction in displayed_account_transactions:
            if dispayed_account_transaction.category.name not in unique_categories:
                unique_categories.append(dispayed_account_transaction.category.name)

        account_choices = []
        for account_type in db_session.query(AccountType):
            account_choices.append((account_type.id, account_type.name))
        add_account_form = AddAccountForm()
        add_account_form.type_id.choices = account_choices
        remove_account_form = RemoveAccountForm()
        upload_form = UploadForm(upload_account_id=account_id)
        return render_template('accounts.html', accounts=user_accounts, displayed_account=account_id,
                               uploads=displayed_account_uploads,
                               transactions=displayed_account_transactions, unique_categories=unique_categories,
                               add_account_form=add_account_form, remove_account_form=remove_account_form,
                               upload_form=upload_form)
    else:
        return redirect(url_for('view_accounts'))


@app.route('/view_accounts/addAccount', methods=['POST'])
@login_required
def add_account():
    form = AddAccountForm()
    type_id = int(form.type_id.data)
    account_name = AccountType.query.filter_by(id=type_id).one().name
    new_account = Account(None, account_name, current_user.id, type_id)
    db_session.add(new_account)
    db_session.commit()

    return redirect(url_for('view_account', account_id=new_account.id))


@app.route('/view_accounts/removeAccount', methods=['POST'])
@login_required
def remove_account():
    form = RemoveAccountForm()

    if form.validate_on_submit():
        account_id = form.remove_account_id.data
        account = Account.query.filter_by(id=account_id).one()
        if account.user_id == current_user.id:
            db_session.delete(account)
            db_session.commit()
            # NEED TO DELETE TRANSACTIONS ASSOCIATED WITH THIS ACCOUNT ALSO
    return redirect(url_for('view_accounts'))


class MyError(Exception):
    pass


def row_cleaner(dirty_row, account):
    # THis function is provided rows from the uploaded CSVs and will return
    # a "clean" data set that we are happy to upload to our transaction database
    dirty_name = dirty_row[account.type.csv_name_column]
    dirty_date = dirty_row[account.type.csv_date_column]
    dirty_date_format = account.type.csv_date_format
    dirty_amount = dirty_row[account.type.csv_amount_column]
    amount_multiplier = account.type.csv_amount_multiple
    #
    clean_name = dirty_name.strip()
    #
    # # convert the date into desired format
    try:
        clean_date = datetime.strptime(dirty_date, dirty_date_format).strftime('%Y-%m-%d')
    except ValueError:
        raise MyError('Incompatible format in date column')
    # # clean the amount string (remove currency symbols and turn into float)
    currency_symbols = ['£', '$', '€']
    try:
        if dirty_amount[0] in currency_symbols:
            dirty_amount = dirty_amount[1:]
        clean_amount = float(dirty_amount)*amount_multiplier
    except ValueError:
        flash('Incompatible format in amounts column')
        return redirect(url_for('view_accounts'))

    clean_row = [clean_name, clean_date, clean_amount]
    return clean_row


def extract_CSV_data(reader, account_id):
    row_counter = 1
    new_transactions = []
    account = Account.query.filter_by(id=account_id).one()
    # Loop through the rows in the CSV and add to transactions table where appropriate
    for row in reader:
        if row_counter >= account.type.csv_first_row:
            try:
                clean_row = row_cleaner(row, account)
            except MyError as exception:
                flash(exception)
                return redirect(url_for('view_accounts'))

            else:
                #             # Now that we know that this row is clean...
                #             # If the transaction doesn't match an already existing record
                #             # then add to session to be uploaded
                if not db_session.query(exists().where(and_(Transaction.name == clean_row[0],
                                                            Transaction.date == clean_row[1],
                                                            Transaction.amount == clean_row[2],
                                                            Transaction.account_id == account_id))).scalar():
                    new_transaction = Transaction(name=clean_row[0], date=clean_row[1], amount=clean_row[2],
                                                  account_id=account_id, user_id=current_user.id)
                    new_transactions.append(new_transaction)
        row_counter += 1
    return new_transactions


@app.route('/view_accounts/uploadFile', methods=['GET', 'POST'])
@login_required
def upload_file():
    form = UploadForm()
    # ADD MAX UPLOAD SIZE
    if form.validate_on_submit():

        f = form.csv_file.data
        filename = secure_filename(f.filename)
        reader = csv.reader(io.StringIO(f.stream.read().decode("UTF8"), newline=None))
        # CHECK IF CSV IS COMPATIBLE

        new_transactions = extract_CSV_data(reader, form.upload_account_id.data)
        upload_count = 0
        # DO PROPER ERROR HANDLING
        if not new_transactions:
            flash('No new transactions added')
        else:
            new_upload = Upload(name=filename, date=datetime.now(), account_id=form.upload_account_id.data,
                                user_id=current_user.id, transactions=new_transactions)
            db_session.add(new_upload)
            for new_transaction in new_transactions:
                db_session.add(new_transaction)
                upload_count += 1
            db_session.commit()
            flash(str(upload_count) + ' transactions successfully uploaded')

        return redirect(url_for('view_account', account_id=form.upload_account_id.data))
    else:
        flash('Upload failed - please try again')
        return redirect(url_for('view_accounts'))


@app.route('/view_accounts/removeUpload', methods=['GET', 'POST'])
@login_required
def remove_upload():
    upload_id = request.form['upload_id']
    upload = Upload.query.filter_by(id=upload_id).one()
    account_id = upload.account_id
    accounts = [a.id for a in db_session.query(Account.id).filter_by(user_id=current_user.id).all()]
    if account_id in accounts:
        db_session.delete(upload)
        db_session.commit()
        flash('Upload deleted successfully')
        return redirect(url_for('view_account', account_id=account_id))
    else:
        flash('There was an error deleting your upload, please try again.')
        return redirect(url_for('view_accounts'))


@app.route('/view_accounts/loadTransactionCategories', methods=['GET'])
@login_required
def load_transaction_categories():
    categories = []
    for category in db_session.query(TransactionCategory):
        categories.append((category.id, category.name))
    return json.dumps(categories)


@app.route('/view_accounts/categoriseTransactions', methods=['POST'])
@login_required
def categorise_transactions():
    data = request.get_json()
    category_id = data['category_id']
    message = 'Failed update'
    counter = 0
    for transaction in data['transactions']:
        transaction_id = int(transaction['id'])
        if isinstance(transaction_id, int):
            try:
                transaction_to_update = db_session.query(Transaction).filter_by(id=transaction_id).one()
                transaction_to_update.category_id = category_id
                transaction_to_update.category_override = 'Y'
                counter += 1
            except:
                message = 'Failed update'
                break

        if counter > 0:
            try:
                db_session.commit()
                message = 'Success'
            except:
                message = 'Failed update'
                break
    return message


@app.route('/view_accounts/categoriseSimilarTransactions', methods=['POST'])
@login_required
def categorise_similar_transactions():

    data = request.get_json()
    category_id = data['category_id']
    transaction_id = data['transactions'][0]['id']
    if isinstance(transaction_id, int) and isinstance(category_id, int):
        try:
            selected_transaction = Transaction.query.filter_by(id=transaction_id).one()
        except:
            raise MyError('Could not find selected transaction')

        if selected_transaction.user_id == current_user.id:
            db_session.query(Transaction).\
                filter(and_(Transaction.name == selected_transaction.name, Transaction.user_id == selected_transaction.user_id)).\
                update({"category_id": category_id, "category_override": 'Y'})
            db_session.commit()
        else:
            raise MyError('Account ids do not match up')
    else:
        raise MyError('Update inputs have been tampered')
    return 'Success'





@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
