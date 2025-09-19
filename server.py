'''from flask import Flask, render_template, request, jsonify
from email_handler import fetch_emails, unsubscribe_sender, load_blocklist

app = Flask(__name__)

# Dummy user credentials (use environment vars in real app)
USERNAME = "enter ur email address"
PASSWORD = "enter ur email password"

@app.route("/")
def home():
    emails = fetch_emails(USERNAME, PASSWORD, limit=5)
    blocklist = load_blocklist()
    return render_template("email_view.html", emails=emails, blocklist=blocklist)

@app.route("/unsubscribe", methods=["POST"])
def unsubscribe():
    sender = request.json.get("sender")
    if unsubscribe_sender(sender):
        return jsonify({"status": "success", "sender": sender})
    return jsonify({"status": "failed"})

if __name__ == "__main__":
    app.run(debug=True)

'''
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from email_handler import fetch_emails, unsubscribe_sender, load_blocklist

app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for session management

@app.route("/", methods=["GET"])
def index():
    if "username" in session and "password" in session:
        return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    # Save to session
    session["username"] = email
    session["password"] = password

    return redirect(url_for("home"))

@app.route("/home")
def home():
    if "username" not in session or "password" not in session:
        return redirect(url_for("index"))

    emails = fetch_emails(session["username"], session["password"], limit=5)
    blocklist = load_blocklist()
    return render_template("email_view.html", emails=emails, blocklist=blocklist)

@app.route("/unsubscribe", methods=["POST"])
def unsubscribe():
    sender = request.json.get("sender")
    if unsubscribe_sender(sender):
        return jsonify({"status": "success", "sender": sender})
    return jsonify({"status": "failed"})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

