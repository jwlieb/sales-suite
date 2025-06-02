from datetime import datetime
from app import db
from app.models import Report, Product, Sale
from .amazon_sp_api import AmazonSPAPIService
import json

class ReportProcessor:
    def __init__(self):
        self.amazon_api = AmazonSPAPIService()

    def process_report(self, report_id):
        """Process a report and store its data"""
        try:
            report = Report.query.get(report_id)
            if not report:
                return False

            # Get report data from Amazon
            report_data = self.amazon_api.get_report_document(report.report_document_id)
            if not report_data:
                return False

            # Process the data based on report type
            if report.type == 'sales':
                processed_data = self._process_sales_report(report_data)
            elif report.type == 'orders':
                processed_data = self._process_orders_report(report_data)
            elif report.type == 'inventory':
                processed_data = self._process_inventory_report(report_data)
            else:
                return False

            # Update report with processed data
            report.data = processed_data
            report.updated_at = datetime.utcnow()
            db.session.commit()

            return True
        except Exception as e:
            current_app.logger.error(f"Error processing report {report_id}: {str(e)}")
            return False

    def _process_sales_report(self, report_data):
        """Process sales report data"""
        try:
            # Process sales data using pandas
            processed_data = self.amazon_api.process_sales_data(report_data)
            
            # Store sales data in database
            for sale in processed_data:
                product = Product.query.filter_by(asin=sale['asin']).first()
                if product:
                    new_sale = Sale(
                        product_id=product.id,
                        date=datetime.strptime(sale['date'], '%Y-%m-%d').date(),
                        quantity=sale['quantity'],
                        revenue=sale['revenue'],
                        marketplace=sale.get('marketplace', 'Unknown')
                    )
                    db.session.add(new_sale)
            
            db.session.commit()
            return processed_data
        except Exception as e:
            current_app.logger.error(f"Error processing sales report: {str(e)}")
            return None

    def _process_orders_report(self, report_data):
        """Process orders report data"""
        try:
            # Process orders data
            orders = []
            for order in report_data.get('Orders', []):
                order_data = {
                    'order_id': order.get('AmazonOrderId'),
                    'purchase_date': order.get('PurchaseDate'),
                    'order_status': order.get('OrderStatus'),
                    'order_total': order.get('OrderTotal', {}).get('Amount', 0),
                    'items': []
                }
                
                # Get order items
                for item in order.get('OrderItems', []):
                    order_data['items'].append({
                        'asin': item.get('ASIN'),
                        'title': item.get('Title'),
                        'quantity': item.get('QuantityOrdered'),
                        'price': item.get('ItemPrice', {}).get('Amount', 0)
                    })
                
                orders.append(order_data)
            
            return orders
        except Exception as e:
            current_app.logger.error(f"Error processing orders report: {str(e)}")
            return None

    def _process_inventory_report(self, report_data):
        """Process inventory report data"""
        try:
            # Process inventory data
            inventory = []
            for item in report_data:
                inventory_data = {
                    'asin': item.get('asin'),
                    'sku': item.get('sku'),
                    'quantity': item.get('quantity'),
                    'condition': item.get('condition'),
                    'last_updated': item.get('last_updated')
                }
                inventory.append(inventory_data)
            
            return inventory
        except Exception as e:
            current_app.logger.error(f"Error processing inventory report: {str(e)}")
            return None 