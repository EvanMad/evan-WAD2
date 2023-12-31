from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, jsonify
from . import db
from flask_login import login_required, current_user
from . import models
from sqlalchemy import func
import json
from .forms import ReviewForm
from .db_manager import *
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Get the timestamp 36 hours ago
    trending_treshold = 36
    timestamp_trending_treshold = datetime.utcnow() - timedelta(hours=trending_treshold)

    # Function calls to get trending data, implemented in db_manager.py

    # Get trending coasters
    trending_rollercoasters_data = get_trending_rollercoasters(timestamp_trending_treshold)

    # Get trending reviews
    trending_review = get_trending_review(timestamp_trending_treshold)

    # Highest-rated rollercoaster
    highest_rated_rollercoasters, average_scores = get_highest_rollercoaster()

    # Most liked users
    most_liked_users = get_most_liked_users()

    return render_template('index.html',
                           trending_rollercoasters_data=trending_rollercoasters_data,
                           trending_review=trending_review,
                           highest_rated_rollercoasters=highest_rated_rollercoasters,
                           most_liked_users=most_liked_users)

@main.route('/profile')
@login_required
def profile():
    # Redirect to view_profile with current_user.id as user_id
    return redirect(url_for('main.view_profile', user_id=current_user.id))

@main.route('/rollercoaster/<rc_id>')
def rollercoaster_page(rc_id):
    rollercoaster = models.Rollercoaster.query.filter_by(id=rc_id).first()
    if rollercoaster:
        # Calculate the average score using the relationship
        average_score = get_average_score(rollercoaster.id)

        # Retrieve reviews using the Rollercoaster relationship
        reviews = rollercoaster.reviews

        return render_template('rollercoaster.html', rollercoaster=rollercoaster, average_score=average_score, reviews=reviews)
    else:
        return render_template('404.html')

@main.route('/assets/<filename>')
def get_image(filename):
    return send_from_directory('assets', filename)

@main.route('/404')
def four_o_four():
    return render_template('404.html')

# Route for viewing each individual review
# !warning deprecated page 
@main.route('/review/<review_id>')
def review_page(review_id):
    db_query = (
        db.session.query(models.Review, models.Rollercoaster, models.User)
        .join(models.Rollercoaster, models.Review.rollercoaster_id == models.Rollercoaster.id)
        .join(models.User, models.Review.user_id == models.User.id)
        .filter(models.Review.id == review_id)
        .all()
    )
    if len(db_query) > 0:
        db_query = db_query[0]
        review = db_query[0]
        if review:
            rollercoaster = db_query[1]
            user = db_query[2]
            return render_template('review.html', review=review, user=user, rollercoaster=rollercoaster)
    return redirect(url_for('main.four_o_four'))

@main.route('/profile/<user_id>')
def view_profile(user_id):

    user = models.User.query.get(user_id)
    if user:
        reviews = user.reviews
        total_reviews = len(reviews)

        try:
            total_likes = sum(review.likes for review in reviews)
        except:
            total_likes = 0

        highest_review = max(reviews, key=lambda review: review.rating, default=None)
        lowest_review = min(reviews, key=lambda review: review.rating, default=None)
        average_review = round(sum(review.rating for review in reviews) / total_reviews, 2) if total_reviews > 0 else None

        return render_template('profile.html', user=user, reviews=reviews, total_reviews=total_reviews, highest_review=highest_review, lowest_review=lowest_review, average_review=average_review, total_likes=total_likes)
    else:
        return redirect(url_for('main.four_o_four'))

@main.route('/rollercoasters', methods=['GET'])
def view_rollercoasters():
    rollercoasters = models.Rollercoaster.query.all()
    data = []
    for rollercoaster in rollercoasters:
        average_score = get_average_score(rollercoaster.id)
        data.append({'rollercoaster': rollercoaster, 'average_score': average_score})
    return render_template('rollercoasters.html', data=data)

@main.route('/users', methods=['GET'])
def view_users():
    users = models.User.query.all()
    return render_template('users.html', users=users)

@login_required
@main.route('/add_review', methods=['GET'])
def add_review():

    rollercoasters = models.Rollercoaster.query.all()

    rollercoasters_names = [item.name for item in rollercoasters]

    form = ReviewForm()
    form.rollercoaster.choices = rollercoasters_names
    return render_template('write_review.html', form=form)

@login_required
@main.route('/add_review', methods=['POST'])
def add_review_post():

    rollercoaster = request.form.get('rollercoaster')
    content = request.form.get('content')
    rating = request.form.get('rating')
    review = round(float(rating), 2)

    rollercoaster_id = models.Rollercoaster.query.filter_by(name=rollercoaster).first().id
    new_review = models.Review(user_id=current_user.id,
                        rollercoaster_id=rollercoaster_id,
                        rating=rating,
                        review_text=content
                        )
    db.session.add(new_review)
    db.session.commit()
    flash("Review Written!", 'alert-success')

    #return redirect(url_for('main.review_page', review_id=new_review.id))
    return redirect(url_for('main.rollercoaster_page', rc_id=rollercoaster_id))

@login_required
@main.route("/add_like", methods=['POST'])
def add_like():
    try:
        review_id = json.loads(request.data)['review_id']
        review = models.Review.query.get(review_id)

        if review:
            review.likes += 1

            like = models.Likes(user_id = current_user.id, review_id=review.id)
            db.session.add(like)

            db.session.commit()

            return jsonify({"likes": review.likes, "status": "success"}), 200
        else:
            return jsonify({"error": "Review not found"}), 404

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@login_required
@main.route("/remove_like", methods=['POST'])
def remove_like():
    try:
        review_id = json.loads(request.data)['review_id']
        review = models.Review.query.filter_by(id=review_id).first()

        if review:
            review.likes -= 1
            
            like = models.Likes.query.filter_by(user_id=current_user.id, review_id=review.id).first()
            db.session.delete(like)

            db.session.commit()

            return jsonify({"likes": review.likes, "status": "success"}), 200
        else:
            return jsonify({"error": "Review not found"}), 404

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500