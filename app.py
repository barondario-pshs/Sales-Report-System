from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "secret_sales_key"

# [Password, Name, Age, Address, Sales, Role]
accounts = {
    "admin": ["123", "System Boss", "30", "Main Office", 0.0, "admin"],
    "cashier1": ["pass123", "Jane Doe", "22", "Counter A", 150.0, "cashier"],
    "cashier2": ["pass456", "John Smith", "25", "Counter B", 0.0, "cashier"],
    "cashier3": ["pass789", "Emily Davis", "28", "Counter C", 0.0, "cashier"],
    "cashier4": ["pass321", "Michael Brown", "24", "Counter D", 0.0, "cashier"],
}

branch_total = 150.0

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form.get("username", "").strip()
        pwd = request.form.get("password")
        if uname in accounts and accounts[uname][0] == pwd:
            return redirect(url_for("records_view", username=uname))
        
        flash("Invalid Credentials. Please try again.", "error")
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form.get("username", "").strip()
        
        # Check if user already exists
        if uname in accounts:
            flash("Username already exists! Choose another.", "error")
            return redirect(url_for("register"))

        accounts[uname] = [
            request.form.get("password"),
            request.form.get("name"),
            request.form.get("age"),
            request.form.get("address"),
            0.0, 
            request.form.get("role")
        ]
        flash("Account Created Successfully!", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/records/<username>", methods=["GET", "POST"])
def records_view(username):
    global branch_total
    if username not in accounts:
        return redirect(url_for("login"))

    user_data = accounts[username]
    
    if request.method == "POST":
        try:
            sale_amt = float(request.form.get("sale_amount", 0))
            accounts[username][4] += sale_amt 
            branch_total += sale_amt
            flash(f"Recorded sale of ${sale_amt:.2f}", "success")
        except:
            flash("Invalid amount entered.", "error")
        return redirect(url_for("records_view", username=username))

    return render_template("records.html", user=user_data, uname=username, all_accounts=accounts, total=branch_total)

@app.route("/update/<username>", methods=["GET", "POST"])
def update_user(username):
    if username not in accounts:
        return redirect(url_for("records_view", username="admin"))
    
    if request.method == "POST":
        # Overwrites the list with new form data, keeps the old sales (index 4)
        accounts[username] = [
            request.form.get("password"),
            request.form.get("name"),
            request.form.get("age"),
            request.form.get("address"),
            accounts[username][4], 
            request.form.get("role")
        ]
        flash(f"Record for {username} updated!", "success")
        return redirect(url_for("records_view", username="admin"))

    # This sends the existing info to pre-fill the update.html form
    return render_template("update.html", uname=username, user=accounts[username])

@app.route("/delete/<username>", methods=["GET", "POST"])
def delete_user(username):
    if username == "admin":
        flash("Cannot delete the master admin!", "error")
        return redirect(url_for("records_view", username="admin"))

    if request.method == "POST":
        # Pag clinick ang "Yes, Delete", dito papasok
        if username in accounts:
            del accounts[username]
            flash(f"User {username} deleted successfully.", "success")
        return redirect(url_for("records_view", username="admin"))

    # Pag GET (clinick lang yung delete link), ipakita ang confirmation page
    return render_template("confirm_delete.html", uname=username)

if __name__ == "__main__":
    app.run(debug=True)
