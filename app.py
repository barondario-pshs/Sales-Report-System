from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
# Secret key is required for 'flash' messages to stay secure during a session
app.secret_key = "secret_sales_key"

# Indices: [0:Password, 1:Name, 2:Age, 3:Address, 4:Sales, 5:Role]
accounts = {
    "admin": ["123", "System Boss", "30", "Main Office", 0.0, "admin"],
    "cashier1": ["pass123", "Jane Doe", "22", "Counter A", 150.0, "cashier"],
    "cashier2": ["pass456", "John Smith", "25", "Counter B", 0.0, "cashier"],
    "cashier3": ["pass789", "Emily Davis", "28", "Counter C", 0.0, "cashier"],
    "cashier4": ["pass321", "Michael Brown", "24", "Counter D", 0.0, "cashier"],
}

# GLOBAL VARIABLE: Tracks total sales across all dictionary entries
branch_total = 150.0

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Pulling data from HTML inputs by their 'name' attributes
        uname = request.form.get("username", "").strip()
        pwd = request.form.get("password", "").strip()
        
        # Validation: Ensure no fields are empty
        if not uname or not pwd:
            flash("Empty field has been detected, please input all login credentials.", "error")
            return redirect(url_for("login"))

        # DICTIONARY LOOKUP: Check if key exists and if index 0 (password) matches
        if uname in accounts and accounts[uname][0] == pwd:
            flash("Login Successful!", "success") 
            # Send the username to the records route to display specific data
            return redirect(url_for("records_view", username=uname))
        
        flash("Invalid Credentials. Please try again.", "error") 
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Grouping inputs into a temp dictionary for easier validation
        data = {
            "username": request.form.get("username", "").strip(),
            "password": request.form.get("password", "").strip(),
            "name": request.form.get("name", "").strip(),
            "age": request.form.get("age", "").strip(),
            "address": request.form.get("address", "").strip()
        }
        
        # Pythonic validation: Check if any value in the dictionary is empty
        empty_fields = [k for k, v in data.items() if not v]
        if empty_fields:
            field_list = ", ".join(empty_fields)
            flash(f"Empty field has been detected, please input your {field_list}.", "error")
            return redirect(url_for("register"))

        # Prevent duplicate keys (usernames) in the dictionary
        if data["username"] in accounts:
            flash("Username already exists!", "error")
            return redirect(url_for("register"))

        # ADDING DATA: Create a new key-value pair in 'accounts'
        accounts[data["username"]] = [
            data["password"], data["name"], data["age"], 
            data["address"], 0.0, request.form.get("role")
        ]
        flash("Account Created Successfully!", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/records/<username>", methods=["GET", "POST"])
def records_view(username):
    global branch_total
    # Security check: If username doesn't exist in our keys, boot to login
    if username not in accounts:
        return redirect(url_for("login"))

    # Accessing the specific List associated with this Username Key
    user_data = accounts[username]
    
    if request.method == "POST":
        raw_amt = request.form.get("sale_amount", "").strip()
        if not raw_amt:
            flash("Empty field has been detected, please input the sale amount.", "error")
            return redirect(url_for("records_view", username=username))
            
        try:
            sale_amt = float(raw_amt)
            if sale_amt < 0:
                flash("Sale amount cannot be negative.", "error")
            else:
                # UPDATING: Adding amount to index 4 (sales) and global total
                accounts[username][4] += sale_amt 
                branch_total += sale_amt
                flash(f"Recorded sale of ${sale_amt:.2f}", "success")
        except ValueError:
            flash("Invalid amount entered. Please enter a valid number.", "error")
        return redirect(url_for("records_view", username=username))

    # PASSING DATA: Sending the dictionary and totals to the HTML template
    return render_template("records.html", user=user_data, uname=username, all_accounts=accounts, total=branch_total)

@app.route("/update/<username>", methods=["GET", "POST"])
def update_user(username):
    global branch_total
    # Guard Clause: Verify user exists before attempting to access index
    if username not in accounts:
        flash("User does not exist.", "error")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        form_data = {
            "password": request.form.get("password", "").strip(),
            "name": request.form.get("name", "").strip(),
            "age": request.form.get("age", "").strip(),
            "address": request.form.get("address", "").strip(),
            "sales": request.form.get("sales", "").strip()
        }
        role = request.form.get("role")

        # Custom validation logic for multiple empty fields
        empty_fields = [k for k, v in form_data.items() if not v]
        if empty_fields:
            if len(empty_fields) == 5:
                flash("Empty field has been detected, please input all of the fields.", "error")
            else:
                field_list = ", ".join(empty_fields)
                flash(f"Empty field has been detected, please input your {field_list}.", "error")
            return redirect(url_for("update_user", username=username))

        try:
            new_sales = float(form_data["sales"])
        except ValueError:
            flash("Invalid sales amount. Please enter a valid number.", "error") 
            return redirect(url_for("update_user", username=username))

        # MATH SYNC: Subtract old sales and add new sales to keep grand total accurate
        old_sales = accounts[username][4]
        branch_total = round((branch_total - old_sales) + new_sales, 2)

        # OVERWRITING: Replacing the old list with updated info for this Key
        accounts[username] = [
            form_data["password"], form_data["name"], form_data["age"],
            form_data["address"], new_sales, role
        ]
        
        flash(f"Record for {username} updated successfully!", "success")
        
        # SMART REDIRECT: Sends user back to their specific dashboard
        return redirect(url_for("records_view", username=username))

    # PRE-FILLING: Sending existing data to the form so user can see current values
    return render_template("update.html", uname=username, user=accounts[username])

@app.route("/delete/<username>", methods=["GET", "POST"])
def delete_user(username):
    global branch_total
    # Protection for the master admin account
    if username == "admin":
        flash("Cannot delete the master admin!", "error")
        return redirect(url_for("records_view", username="admin"))

    if request.method == "POST":
        if username in accounts:
            # FINANCIAL CLEANUP: Deduct user sales from total before removing them
            branch_total -= accounts[username][4]
            # DELETING: Remove the entire Key-Value pair from the dictionary
            del accounts[username]
            flash(f"User {username} deleted successfully.", "success") 
        return redirect(url_for("records_view", username="admin"))

    return render_template("confirm_delete.html", uname=username)

if __name__ == "__main__":
    # Runs the server in debug mode for real-time code updates
    app.run(debug=True)