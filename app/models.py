from datetime import datetime
from . import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asin = db.Column(db.String(10), unique=True, nullable=False)
    title = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sales = db.relationship('Sale', backref='product', lazy=True)
    competitor_prices = db.relationship('CompetitorPrice', backref='product', lazy=True)
    profit_margins = db.relationship('ProfitMargin', backref='product', lazy=True)
    keywords = db.relationship('KeywordPerformance', backref='product', lazy=True)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    revenue = db.Column(db.Float, nullable=False)
    marketplace = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # daily, weekly, monthly
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CompetitorPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    competitor_asin = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    shipping_price = db.Column(db.Float, default=0.0)
    is_prime = db.Column(db.Boolean, default=False)
    is_fba = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    condition = db.Column(db.String(50), default='New')

class ProfitMargin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    amazon_fees = db.Column(db.Float, nullable=False)
    shipping_cost = db.Column(db.Float, nullable=False)
    product_cost = db.Column(db.Float, nullable=False)
    storage_fees = db.Column(db.Float, default=0.0)
    advertising_cost = db.Column(db.Float, default=0.0)
    returns_cost = db.Column(db.Float, default=0.0)
    net_profit = db.Column(db.Float, nullable=False)
    margin_percentage = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class KeywordPerformance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    keyword = db.Column(db.String(255), nullable=False)
    search_rank = db.Column(db.Integer)
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)
    ctr = db.Column(db.Float, default=0.0)  # Click-through rate
    acos = db.Column(db.Float, default=0.0)  # Advertising Cost of Sales
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
