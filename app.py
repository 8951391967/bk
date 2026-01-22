

import json
import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "banking_secret_key"

DATA_FILE = 'accounts.json'

def load_data():
    
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_data(data):
   
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)


accounts = load_data()

@app.route('/')
def index():
    
    highest_acc = None
    if accounts:
        highest_acc_num = max(accounts, key=lambda x: accounts[x]['balance'])
        highest_acc = {"acc_num": highest_acc_num, **accounts[highest_acc_num]}
        
    return render_template('index.html', accounts=accounts, highest_acc=highest_acc)

@app.route('/create', methods=['POST'])
def create_account():
    name = request.form.get('name')
    acc_num = request.form.get('acc_num')
    try:
        balance = float(request.form.get('balance', 0))
        if acc_num in accounts:
            flash("Error: Account number already exists!")
        else:
            accounts[acc_num] = {'name': name, 'balance': balance}
            save_data(accounts)
            flash(f"Account for {name} created successfully!")
    except ValueError:
        flash("Invalid balance amount.")
    return redirect(url_for('index'))

@app.route('/transaction', methods=['POST'])
def transaction():
    acc_num = request.form.get('acc_num')
    amount = float(request.form.get('amount', 0))
    action = request.form.get('action')

    if acc_num not in accounts:
        flash("Error: Account not found!")
        return redirect(url_for('index'))

    if action == 'deposit':
        accounts[acc_num]['balance'] += amount
        save_data(accounts) 
        flash(f"Deposited {amount:.2f} successfully.")
    
    elif action == 'withdraw':
        if amount > accounts[acc_num]['balance']:
            flash("Error: Insufficient balance!")
        else:
            accounts[acc_num]['balance'] -= amount
            save_data(accounts) # Save to JSON
            flash(f"Withdrew {amount:.2f} successfully.")
            
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)