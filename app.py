from flask import Flask, render_template, request, redirect, url_for, flash
from controllers.auth_controller import AuthController
from flask import session
from models.user_model import UserModel
app = Flask(__name__)
app.secret_key = "your_secret_key"  # For flash messages

# Routes
@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    return AuthController.register()

@app.route("/login", methods=["GET", "POST"])
def login():
    return AuthController.login()

@app.route("/logout")
def logout():
    return AuthController.logout()

@app.route("/dashboard")
def dashboard():
    # Check if the user is logged in
    if "user" not in session:
        flash("Please log in to access the dashboard.")
        return redirect("/login")

    user = session["user"]


    balance = UserModel.get_user(user["username"])["balance"]  # Fetch the user's balance
    return render_template("dashboard.html", user=user, balance=balance)

@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    if "user" not in session:
        flash("Please log in to access this feature.")
        return redirect("/login")

    if request.method == "POST":
        amount = request.form.get("amount", type=float)
        if amount <= 0:
            flash("Deposit amount must be greater than 0.")
            return render_template("deposit.html")

        user = session["user"]
        current_balance = UserModel.get_user(user["username"])["balance"]
        new_balance = current_balance + amount
        UserModel.update_balance(user["username"], new_balance)

        flash(f"Successfully deposited ${amount:.2f}.")
        return redirect("/dashboard")

    return render_template("deposit.html")


@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    if "user" not in session:
        flash("Please log in to access this feature.")
        return redirect("/login")

    if request.method == "POST":
        amount = request.form.get("amount", type=float)
        user = session["user"]
        current_balance = UserModel.get_user(user["username"])["balance"]

        if amount <= 0:
            flash("Withdrawal amount must be greater than 0.")
            return render_template("withdraw.html")

        if amount > current_balance:
            flash("Insufficient funds.")
            return render_template("withdraw.html")

        new_balance = current_balance - amount
        UserModel.update_balance(user["username"], new_balance)

        flash(f"Successfully withdrew ${amount:.2f}.")
        return redirect("/dashboard")

    return render_template("withdraw.html")


@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    if "user" not in session:
        flash("Please log in to access this feature.")
        return redirect("/login")

    if request.method == "POST":
        recipient_username = request.form.get("recipient_username")
        amount = request.form.get("amount", type=float)

        if amount <= 0:
            flash("Transfer amount must be greater than 0.")
            return render_template("transfer.html")

        user = session["user"]
        current_balance = UserModel.get_user(user["username"])["balance"]

        if amount > current_balance:
            flash("Insufficient funds.")
            return render_template("transfer.html")

        recipient = UserModel.get_user(recipient_username)
        if not recipient:
            flash("Recipient username does not exist.")
            return render_template("transfer.html")

        # Update balances
        UserModel.update_balance(user["username"], current_balance - amount)
        UserModel.update_balance(recipient_username, recipient["balance"] + amount)

        flash(f"Successfully transferred ${amount:.2f} to {recipient_username}.")
        return redirect("/dashboard")

    return render_template("transfer.html")

@app.route("/send_money", methods=["GET", "POST"])
def send_money():
    if "user" not in session:
        flash("Please log in to access this feature.")
        return redirect("/login")

    if request.method == "POST":
        external_account = request.form.get("external_account")
        amount = request.form.get("amount", type=float)
        transaction_fee = 2.5  # Flat transaction fee for external transfers

        if amount <= 0:
            flash("Transfer amount must be greater than 0.")
            return render_template("send_money.html")

        user = session["user"]
        current_balance = UserModel.get_user(user["username"])["balance"]

        if amount + transaction_fee > current_balance:
            flash("Insufficient funds for this transfer.")
            return render_template("send_money.html")

        # Deduct amount + fee from the user's account
        new_balance = current_balance - (amount + transaction_fee)
        UserModel.update_balance(user["username"], new_balance)

        flash(f"Successfully transferred ${amount:.2f} to external account '{external_account}' with a ${transaction_fee:.2f} fee.")
        return redirect("/dashboard")

    return render_template("send_money.html")

@app.route("/accounts", methods=["GET", "POST"])
def accounts():
    if "user" not in session:
        flash("Please log in to access this feature.")
        return redirect("/login")

    user = session["user"]
    accounts = UserModel.get_accounts(user["username"])  # Fetch all accounts for the user

    return render_template("accounts.html", accounts=accounts)

# Accounts
@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if "user" not in session:
        flash("Please log in to access this feature.")
        return redirect("/login")

    if request.method == "POST":
        account_name = request.form.get("account_name")
        initial_balance = request.form.get("initial_balance", type=float)
        user = session["user"]

        if initial_balance < 0:
            flash("Initial balance cannot be negative.")
            return render_template("create_account.html")

        UserModel.add_account(user["username"], account_name, initial_balance)
        flash(f"Account '{account_name}' created successfully with an initial balance of ${initial_balance:.2f}.")
        return redirect("/accounts")

    return render_template("create_account.html")


if __name__ == "__main__":
    app.run(debug=True)