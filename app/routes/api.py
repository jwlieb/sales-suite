from flask import Blueprint, jsonify, request, current_app
from ..models import Product, Sale, Report
from ..services.amazon_sp_api import AmazonSPAPIService
from ..services.report_processor import ReportProcessor
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