from . import db
from flask_login import UserMixin
from datetime import datetime
# User and Rollercoaster are a many-to-many relationship. Review is used to bridge the gap between them.
# User and Review (for likes) are a many-to-many relationship. Review is used to bridge the gap between them.


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

    reviews = db.relationship('Review', lazy=True, back_populates='user')
    liked_reviews = db.relationship('Review', secondary='likes', back_populates='liked_by_users')


class Rollercoaster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    year = db.Column(db.Integer)
    height = db.Column(db.Float)
    length = db.Column(db.Float)
    manufacturer = db.Column(db.String(100))
    model = db.Column(db.String(100))
    inversions = db.Column(db.Integer)
    speed = db.Column(db.Float)

    reviews = db.relationship('Review', lazy=True)


class Likes(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False, primary_key=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Define relationships
    user = db.relationship('User', backref=db.backref('user_likes', lazy='dynamic'))
    review = db.relationship('Review', backref=db.backref('review_likes', lazy='dynamic'))


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rollercoaster_id = db.Column(db.Integer, db.ForeignKey('rollercoaster.id'), nullable=False)
    rating = db.Column(db.Float)
    review_text = db.Column(db.String(400))
    likes = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('user_reviews', lazy=True))
    rollercoaster = db.relationship('Rollercoaster', backref=db.backref('coaster_reviews', lazy=True))
    liked_by_users = db.relationship('User', secondary='likes', back_populates='liked_reviews')
