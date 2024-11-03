from flask import render_template, request, flash, redirect, url_for, Blueprint
from flask_login import login_user, login_required, logout_user
from .models import User, db
from .forms import RegistrationForm, LoginForm
from .news_utils import fetch_news_articles, preprocess_text, detect_duplicates, get_default_news

News_API_KEY = "d8f46f24488d469f82ef0f1987fb91e1"
Newsdata_API_KEY = "pub_440061d1f1fe64f7148fd8824c34326aaf6d6"

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    default_news = get_default_news(News_API_KEY, Newsdata_API_KEY)  # Fetch default news items
    return render_template("index.html", news_items=default_news)

@main_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Your account is now created! You are now able to log in", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html", form=form)

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("You have been logged in!", "success")
            return redirect(url_for("main.home"))
        else:
            flash("Login Unsuccessful. Please check username and password", "danger")
    return render_template("login.html", form=form)

@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out!", "info")
    return redirect(url_for("main.home"))

@main_bp.route("/news", methods=["POST"])
def news():
    category = request.form["category"]
    valid_categories = {"business", "entertainment", "health", "science", "sports", "technology", "education", "politics"}
    if category not in valid_categories:
        return "Invalid category", 400
    news_articles = fetch_news_articles(News_API_KEY, Newsdata_API_KEY, category, page_size=40) 
    if news_articles:
        return render_template("news.html", articles=news_articles)
    else:
        return "No news for the selected category.", 404

@main_bp.route("/detect_duplicates", methods=["POST"])
def detect_duplicates_route():
    category = request.form["category"]
    news_articles = fetch_news_articles(News_API_KEY, Newsdata_API_KEY, category)
    preprocessed_articles = [{"title": preprocess_text(article['title']), 'description': preprocess_text(article['description'])} for article in news_articles]
    duplicate_pairs = detect_duplicates(preprocessed_articles)
    return render_template("duplicates.html", duplicate_pairs=duplicate_pairs)
