from flask import Blueprint, render_template
from ..models import Product, Sale, Report
from datetime import datetime, timedelta

bp = Blueprint('views', __name__)

@bp.route('/')
def index():
    # Get summary statistics
    total_products = Product.query.count()
    total_sales = Sale.query.count()
    
    # Get sales for the last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_sales = Sale.query.filter(Sale.date >= thirty_days_ago).all()
    total_revenue = sum(sale.revenue for sale in recent_sales)
    
    return render_template('index.html',
                         total_products=total_products,
                         total_sales=total_sales,
                         total_revenue=total_revenue)

@bp.route('/reports')
def reports():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('reports.html', reports=reports)

@bp.route('/products')
def products():
    products = Product.query.all()
    return render_template('products.html', products=products) 