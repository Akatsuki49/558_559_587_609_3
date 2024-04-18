from flask import Flask, request, session, redirect, url_for, render_template
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
database = client["Inventory"]

server = Flask(__name__)
server.secret_key = "1234"


@server.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@server.route("/register", methods=["POST", "GET"])
def register():
    error = None
    try:
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            user_collection = database.get_collection("users")
            user = user_collection.find_one({"username": username})
            if user:
                error = "Username already exists. Please choose another."
            else:
                user_collection.insert_one({"username": username, "password": password})
                return redirect(url_for("login"))
    except Exception as e:
        error = "An error occurred. Please try again."
    return render_template("register.html", error=error)


@server.route("/login", methods=["POST", "GET"])
def login():
    error = None
    try:
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            user_collection = database.get_collection("users")
            user = user_collection.find_one(
                {"username": username, "password": password}
            )
            if user:
                session["username"] = username
                session["type"] = "customer"
                return redirect(url_for("home", username=username))

            admin_collection = database.get_collection("admin")
            admin = admin_collection.find_one(
                {"username": username, "password": password}
            )
            if admin:
                session["username"] = username
                session["type"] = "admin"
                return redirect(url_for("inventory", username=username))
            else:
                error = "Incorrect username or password. Please try again."
    except Exception as e:
        error = "An error occurred. Please try again."
    return render_template("login.html", error=error)


@server.route("/home/<username>", methods=["GET", "POST"])
def home(username):
    watches = database.get_collection("watches")

    watch_list = list(watches.find())
    print(watch_list)
    name = username
    return render_template("home.html", username=name, watches=watch_list)


@server.route("/inventory/<username>", methods=["GET", "POST"])
def inventory(username):
    name = username
    watches = database.get_collection("watches")

    if request.method == "POST":
        model = request.form["model"]
        brand = request.form["brand"]
        stock = request.form["stock"]
        price = request.form["price"]
        description = request.form["description"]
        image = "https://images-cdn.ubuy.co.in/6537918bb0cbde4d66135ca0-rolex-oyster-perpetual-41mm-automatic.jpg"

        watches.insert_one(
            {
                "model": model,
                "brand": brand,
                "stock": stock,
                "price": price,
                "description": description,
                "image": image,
            }
        )

    watch_list = list(watches.find())
    print(watch_list)
    return render_template("inventory.html", username=name, watches=watch_list)


@server.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    server.run(debug=True)