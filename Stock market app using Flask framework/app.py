import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    try:
        username = db.execute(
            "SELECT username FROM users WHERE id=?", session["user_id"]
        )[0].get("username")
        current_balance = float(
            db.execute("SELECT cash FROM users WHERE id=?", session["user_id"])[0].get(
                "cash"
            )
        )

    except IndexError:
        return redirect("/login")

    try:
        shares = db.execute("SELECT * FROM stocks WHERE owner=?", username)

        # updating current share price to market value
        total_worth_stocks = 0
        for share in shares:
            current_price = float(lookup(share.get("symbol")).get("price"))
            share["current_price"] = current_price
            total_worth_stocks += current_price * share["shares"]

    # handles when user has no shares
    except IndexError:
        shares = {"symbol": "", "shares": "", "price": "", "total": ""}
        total_worth_stocks = 0
        tally = current_balance + total_worth_stocks
        return render_template(
            "index_fresh.html",
            balance=current_balance,
            stocks=shares,
            total_stock_worth=total_worth_stocks,
            tally=tally,
        )
    tally = current_balance + total_worth_stocks
    return render_template(
        "index.html", balance=current_balance, stocks=shares, tally=tally
    )


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    username = db.execute("SELECT username FROM users WHERE id=?", session["user_id"])[
        0
    ].get("username")
    history = db.execute(
        "SELECT * FROM history WHERE owner=? ORDER BY Transacted DESC", username
    )
    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        quoted_dict = lookup(symbol)
        print(quoted_dict)
        if isinstance(quoted_dict, dict):
            return render_template("quoted.html", placeholder=quoted_dict)
        else:
            return apology("Symbol not found", 400)
    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # get username and password from the form
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if len(username) == 0 or len(password) == 0 or len(confirmation) == 0:
            return apology("All fields are required", 400)

        usernames_in_database = db.execute("SELECT username FROM users")
        if username in [uname.get("username") for uname in usernames_in_database]:
            return apology("user already exists, please login", 400)

        if password == confirmation:
            hash = generate_password_hash(password)
            db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)", username, hash
            )
            return redirect("/")
        else:
            return apology("passwords do not match, try again", 400)
    return render_template("register.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        quoted_dict = lookup(symbol)

        # check if quote is valid before getting its price
        if not isinstance(quoted_dict, dict):
            return apology("Please enter valid symbol")
        else:
            cost_per_share = float(quoted_dict.get("price"))

        # check if user entered vaild number of shares before adding it to the database
        noOFshares = request.form.get("shares")

        if noOFshares.isdigit():
            if int(noOFshares) > 0:
                # get username and current balance for user
                noOFshares = int(noOFshares)
                username = db.execute(
                    "SELECT username FROM users WHERE id=?", session["user_id"]
                )[0].get("username")
                deductable = float(cost_per_share * noOFshares)
                current_balance = float(
                    db.execute("SELECT cash FROM users WHERE id=?", session["user_id"])[
                        0
                    ].get("cash")
                )

                # check if user can afford the shares
                if deductable <= current_balance:
                    updated_balance = current_balance - deductable

                    # update database with new balance
                    db.execute(
                        "UPDATE users SET cash=? WHERE username=?",
                        updated_balance,
                        username,
                    )

                    # check if stock exists and update shares else create new entry in database
                    stock_existingInDB = db.execute(
                        "SELECT * FROM stocks WHERE symbol=? AND owner=?",
                        symbol,
                        username,
                    )
                    if len(stock_existingInDB) != 0:
                        # get already owned number of shares of the stock selected
                        existing_noOfshares = int(stock_existingInDB[0].get("shares"))
                        # if share alredy exists, then
                        updated_shares = existing_noOfshares + noOFshares
                        db.execute(
                            "UPDATE stocks SET shares=? WHERE symbol=? AND owner=?",
                            updated_shares,
                            symbol,
                            username,
                        )
                    else:
                        db.execute(
                            "INSERT INTO stocks (symbol, shares, owner) VALUES (?, ?, ?)",
                            symbol,
                            noOFshares,
                            username,
                        )

                    # logging transaction in history
                    timestamp = db.execute("SELECT CURRENT_TIMESTAMP")[0].get(
                        "CURRENT_TIMESTAMP"
                    )
                    db.execute(
                        "INSERT INTO history (symbol, shares, price, transacted, owner) VALUES (?, ?, ?, ?, ?)",
                        symbol,
                        noOFshares,
                        deductable,
                        timestamp,
                        username,
                    )
                    return redirect("/")

                else:
                    return apology(
                        "Balance too low to purchase any shares. Sell some shares or replenish balance."
                    )
            else:
                return apology("Enter positive integers only", 400)
        else:
            return apology(
                "Please numeric digits only. Partial and non-digits not allowed", 400
            )

    return render_template("buy.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        # retrieve share user wants to sell
        symbol = request.form.get("symbol")
        # get the latest cost per share using the lookup function
        quoted_dict = lookup(symbol)
        cost_per_share = float(quoted_dict.get("price"))

        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("Please enter integer or numeric values only")

        # get the existing number of shares the user owns
        username = db.execute(
            "SELECT username FROM users WHERE id=?", session["user_id"]
        )[0].get("username")
        existing_number_of_shares = int(
            db.execute(
                "SELECT shares FROM stocks WHERE symbol=? AND owner=?", symbol, username
            )[0].get("shares")
        )
        print(
            f"currently user {username} owns {existing_number_of_shares} shares for the stock {symbol}"
        )

        # if shares to be sold is positive integer and less/equal to the currently owned shares then proceed with sale
        if shares > 0 and shares <= existing_number_of_shares:
            # Sale Transaction: update balance by adding the amount of sold shares to user's current balance
            selling_price = cost_per_share * shares
            print("selling price : ", selling_price)

            # logging transaction in history
            timestamp = db.execute("SELECT CURRENT_TIMESTAMP")[0].get(
                "CURRENT_TIMESTAMP"
            )
            db.execute(
                "INSERT INTO history (symbol, shares, price, transacted, owner) VALUES (?, ?, ?, ?, ?)",
                symbol,
                shares * -1,
                selling_price,
                timestamp,
                username,
            )

            # add cash made by selling to current balance
            current_balance = float(
                db.execute("SELECT cash FROM users WHERE id=?", session["user_id"])[
                    0
                ].get("cash")
            )
            updated_balance = (
                current_balance + selling_price
            )  # subtract here because selling price is already negative - so it actually means addition
            print("updated_balance: ", updated_balance)
            # update current balance of user after deduction
            db.execute(
                "UPDATE users SET cash=? WHERE username=?", updated_balance, username
            )

            # removing stock sold from the database
            if existing_number_of_shares == shares:
                db.execute(
                    "DELETE FROM stocks WHERE symbol=? AND owner=?", symbol, username
                )
            else:
                db.execute(
                    "UPDATE stocks SET shares=? WHERE symbol=? AND owner=?",
                    shares,
                    symbol,
                    username,
                )
            return redirect("/")
        else:
            return apology(
                "Number of shares entered must be positive and less than or equal to the current number of shares available.",
                400,
            )

    username = db.execute("SELECT username FROM users WHERE id=?", session["user_id"])[
        0
    ].get("username")
    stocks = db.execute("SELECT * FROM stocks WHERE owner=?", username)
    return render_template("sell.html", stocks=stocks)


# login JB 12345
