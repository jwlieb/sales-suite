from flask import Blueprint, jsonify, request, current_app
from ..models import Product, Sale, Report, CompetitorPrice, ProfitMargin, KeywordPerformance
from ..services.amazon_sp_api import AmazonSPAPIService
from ..services.report_processor import ReportProcessor
from ..services.competitor_tracker import CompetitorTracker
from ..services.profit_calculator import ProfitCalculator
from ..services.keyword_tracker import KeywordTracker
from .. import db
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api')
amazon_api = AmazonSPAPIService()
report_processor = ReportProcessor()

@bp.route('/sales', methods=['GET'])
def get_sales():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({'error': 'start_date and end_date are required'}), 400
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    sales = Sale.query.filter(
        Sale.date >= start_date,
        Sale.date <= end_date
    ).all()
    
    return jsonify([{
        'id': sale.id,
        'product_asin': sale.product.asin,
        'date': sale.date.isoformat(),
        'quantity': sale.quantity,
        'revenue': sale.revenue,
        'marketplace': sale.marketplace
    } for sale in sales])

@bp.route('/reports', methods=['GET'])
def get_reports():
    reports = Report.query.all()
    return jsonify([{
        'id': report.id,
        'name': report.name,
        'type': report.type,
        'start_date': report.start_date.isoformat(),
        'end_date': report.end_date.isoformat(),
        'created_at': report.created_at.isoformat()
    } for report in reports])

@bp.route('/reports', methods=['POST'])
def create_report():
    data = request.form
    
    try:
        report = Report(
            name=data['name'],
            type=data['type'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        )
        db.session.add(report)
        db.session.commit()
        
        # Request report from Amazon
        if report.type == 'sales':
            amazon_report = amazon_api.get_sales_report(report.start_date, report.end_date)
        elif report.type == 'orders':
            amazon_report = amazon_api.get_orders_report(report.start_date, report.end_date)
        elif report.type == 'inventory':
            amazon_report = amazon_api.get_inventory_report()
        else:
            return jsonify({'error': 'Invalid report type'}), 400
        
        if amazon_report:
            report.report_document_id = amazon_report.get('reportDocumentId')
            db.session.commit()
            
            # Process report asynchronously
            report_processor.process_report(report.id)
            
            return jsonify({'success': True, 'report_id': report.id})
        
        return jsonify({'error': 'Failed to create report'}), 500
    except Exception as e:
        current_app.logger.error(f"Error creating report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    report = Report.query.get_or_404(report_id)
    return jsonify({
        'id': report.id,
        'name': report.name,
        'type': report.type,
        'start_date': report.start_date.isoformat(),
        'end_date': report.end_date.isoformat(),
        'data': report.data,
        'created_at': report.created_at.isoformat(),
        'updated_at': report.updated_at.isoformat()
    })

@bp.route('/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/products/<asin>', methods=['GET'])
def get_product(asin):
    product = Product.query.filter_by(asin=asin).first()
    if not product:
        # Try to fetch from Amazon
        amazon_product = amazon_api.get_product_details(asin)
        if amazon_product:
            product = Product(
                asin=asin,
                title=amazon_product.get('title', 'Unknown')
            )
            db.session.add(product)
            db.session.commit()
        else:
            return jsonify({'error': 'Product not found'}), 404
    
    return jsonify({
        'asin': product.asin,
        'title': product.title,
        'total_sales': len(product.sales),
        'total_revenue': sum(sale.revenue for sale in product.sales)
    })

@bp.route('/products/<int:product_id>/competitors', methods=['GET'])
def get_competitors(product_id):
    """Get competitor information for a product."""
    product = Product.query.get_or_404(product_id)
    tracker = CompetitorTracker(AmazonSPAPIService({}))  # Pass your credentials here
    
    # Get market position
    market_position = tracker.get_market_position(product_id)
    
    # Get price alerts
    alerts = tracker.get_price_alerts(product_id)
    
    # Get price history
    history = tracker.get_price_history(product_id)
    
    return jsonify({
        'market_position': market_position,
        'alerts': alerts,
        'history': [{
            'competitor_asin': p.competitor_asin,
            'price': p.price,
            'timestamp': p.timestamp.isoformat(),
            'is_prime': p.is_prime,
            'is_fba': p.is_fba
        } for p in history]
    })

@bp.route('/products/<int:product_id>/profit', methods=['GET'])
def get_profit_analysis(product_id):
    """Get profit analysis for a product."""
    product = Product.query.get_or_404(product_id)
    calculator = ProfitCalculator(AmazonSPAPIService({}))  # Pass your credentials here
    
    # Get profit trends
    trends = calculator.get_profit_trends(product_id)
    
    # Get overall performance
    performance = calculator.get_product_performance(product_id)
    
    return jsonify({
        'trends': [{
            'date': t.date.isoformat(),
            'margin_percentage': t.margin_percentage,
            'net_profit': t.net_profit,
            'total_costs': t.amazon_fees + t.shipping_cost + t.product_cost + 
                          t.storage_fees + t.advertising_cost + t.returns_cost
        } for t in trends],
        'performance': performance
    })

@bp.route('/products/<int:product_id>/keywords', methods=['GET'])
def get_keyword_analysis(product_id):
    """Get keyword analysis for a product."""
    product = Product.query.get_or_404(product_id)
    tracker = KeywordTracker(AmazonSPAPIService({}))  # Pass your credentials here
    
    # Get keyword trends
    trends = tracker.get_keyword_trends(product_id)
    
    # Get top keywords
    top_keywords = tracker.get_top_keywords(product_id)
    
    # Get opportunities
    opportunities = tracker.get_keyword_opportunities(product_id)
    
    # Get keyword health
    health = tracker.get_keyword_health(product_id)
    
    return jsonify({
        'trends': [{
            'keyword': t.keyword,
            'date': t.date.isoformat(),
            'rank': t.search_rank,
            'impressions': t.impressions,
            'clicks': t.clicks,
            'conversions': t.conversions,
            'ctr': t.ctr,
            'acos': t.acos
        } for t in trends],
        'top_keywords': [{
            'keyword': k.keyword,
            'conversions': k.conversions,
            'ctr': k.ctr,
            'acos': k.acos
        } for k in top_keywords],
        'opportunities': opportunities,
        'health': health
    })

@bp.route('/products/<int:product_id>/track', methods=['POST'])
def track_product(product_id):
    """Start tracking a product's competitors, profits, and keywords."""
    product = Product.query.get_or_404(product_id)
    
    # Initialize services
    sp_api = AmazonSPAPIService({})  # Pass your credentials here
    competitor_tracker = CompetitorTracker(sp_api)
    profit_calculator = ProfitCalculator(sp_api)
    keyword_tracker = KeywordTracker(sp_api)
    
    # Track everything
    competitor_success = competitor_tracker.track_competitor_prices(product)
    profit_success = profit_calculator.calculate_profit_margin(product) is not None
    keyword_success = keyword_tracker.track_keyword_performance(product)
    
    return jsonify({
        'success': all([competitor_success, profit_success, keyword_success]),
        'competitor_tracking': competitor_success,
        'profit_tracking': profit_success,
        'keyword_tracking': keyword_success
    }) 