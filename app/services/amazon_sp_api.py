from sp_api.api import Reports, Orders, Catalog, Products
from sp_api.base import Marketplaces
from datetime import datetime, timedelta
from flask import current_app
import pandas as pd
import json
from app import db
from app.models import Product, Sale, Report

class AmazonSPAPIService:
    def __init__(self):
        self.credentials = {
            'refresh_token': current_app.config['AMAZON_REFRESH_TOKEN'],
            'lwa_app_id': current_app.config['AMAZON_CLIENT_ID'],
            'lwa_client_secret': current_app.config['AMAZON_CLIENT_SECRET'],
            'aws_access_key': current_app.config['AMAZON_AWS_ACCESS_KEY'],
            'aws_secret_key': current_app.config['AMAZON_AWS_SECRET_KEY'],
            'role_arn': current_app.config['AMAZON_ROLE_ARN'],
        }
        self.marketplace_id = current_app.config['AMAZON_MARKETPLACE_ID']
        self.reports_api = Reports(credentials=self.credentials)
        self.orders_api = Orders(credentials=self.credentials)
        self.catalog_api = Catalog(credentials=self.credentials)
        self.marketplace = Marketplaces.US  # Default to US marketplace

    def get_sales_report(self, start_date, end_date):
        """Fetch sales report for the specified date range"""
        try:
            report_type = 'GET_FLAT_FILE_OPEN_LISTINGS_DATA'
            response = self.reports_api.create_report(
                reportType=report_type,
                dataStartTime=start_date,
                dataEndTime=end_date,
                marketplaceIds=[self.marketplace_id]
            )
            return response.payload
        except Exception as e:
            current_app.logger.error(f"Error fetching sales report: {str(e)}")
            return None

    def get_orders_report(self, start_date, end_date):
        """Fetch orders report for the specified date range"""
        try:
            report_type = 'GET_FLAT_FILE_OPEN_LISTINGS_DATA'
            response = self.reports_api.create_report(
                reportType=report_type,
                dataStartTime=start_date,
                dataEndTime=end_date,
                marketplaceIds=[self.marketplace_id]
            )
            return response.payload
        except Exception as e:
            current_app.logger.error(f"Error fetching orders report: {str(e)}")
            return None

    def get_inventory_report(self):
        """Fetch current inventory levels"""
        try:
            report_type = 'GET_FLAT_FILE_OPEN_LISTINGS_DATA'
            response = self.reports_api.create_report(
                reportType=report_type,
                marketplaceIds=[self.marketplace_id]
            )
            return response.payload
        except Exception as e:
            current_app.logger.error(f"Error fetching inventory report: {str(e)}")
            return None

    def get_report_document(self, report_document_id):
        """Fetch the actual report document using the report document ID"""
        try:
            response = self.reports_api.get_report_document(report_document_id)
            return response.payload
        except Exception as e:
            current_app.logger.error(f"Error fetching report document: {str(e)}")
            return None

    def get_product_details(self, asin):
        """Fetch product details using the Catalog API"""
        try:
            response = self.catalog_api.get_catalog_item(asin)
            return response.payload
        except Exception as e:
            current_app.logger.error(f"Error fetching product details: {str(e)}")
            return None

    def get_recent_orders(self, days=30):
        """Fetch recent orders"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            response = self.orders_api.get_orders(
                CreatedAfter=start_date.isoformat(),
                MarketplaceIds=[self.marketplace_id]
            )
            return response.payload
        except Exception as e:
            current_app.logger.error(f"Error fetching recent orders: {str(e)}")
            return None

    def process_sales_data(self, report_data):
        """Process sales report data into a structured format"""
        try:
            # Convert report data to DataFrame
            df = pd.DataFrame(report_data)
            
            # Group by date and calculate metrics
            daily_sales = df.groupby('date').agg({
                'quantity': 'sum',
                'revenue': 'sum'
            }).reset_index()
            
            return daily_sales.to_dict('records')
        except Exception as e:
            current_app.logger.error(f"Error processing sales data: {str(e)}")
            return None

    def get_report_status(self, report_id):
        """Check the status of a report"""
        try:
            response = self.reports_api.get_report(report_id)
            return response.payload
        except Exception as e:
            current_app.logger.error(f"Error checking report status: {str(e)}")
            return None

    def list_reports(self, report_types=None, processing_statuses=None):
        """List available reports with optional filters"""
        try:
            params = {
                'marketplaceIds': [self.marketplace_id]
            }
            if report_types:
                params['reportTypes'] = report_types
            if processing_statuses:
                params['processingStatuses'] = processing_statuses

            response = self.reports_api.get_reports(**params)
            return response.payload
        except Exception as e:
            current_app.logger.error(f"Error listing reports: {str(e)}")
            return None

    def get_competing_offers(self, asin: str):
        """Get competing offers for a product."""
        try:
            products_api = Products(credentials=self.credentials, marketplace=self.marketplace)
            response = products_api.get_competitive_pricing_for_asin(asin)
            
            if not response.payload:
                return []

            offers = []
            for item in response.payload:
                if 'Product' in item and 'CompetitivePricing' in item['Product']:
                    for offer in item['Product']['CompetitivePricing'].get('CompetitivePrices', []):
                        if 'Price' in offer:
                            offers.append({
                                'asin': item['Product']['Identifiers']['MarketplaceASIN']['ASIN'],
                                'price': float(offer['Price']['LandedPrice']['Amount']),
                                'shipping_price': float(offer['Price'].get('Shipping', {}).get('Amount', 0)),
                                'is_prime': offer.get('condition', '') == 'New',
                                'is_fba': 'FBA' in offer.get('fulfillmentChannel', ''),
                                'condition': offer.get('condition', 'New')
                            })
            return offers
        except Exception as e:
            print(f"Error getting competing offers: {str(e)}")
            return []

    def get_keyword_performance(self, asin: str, keyword: str):
        """Get keyword performance data for a product."""
        try:
            # This would typically use Amazon's Advertising API
            # For now, we'll simulate the data
            return {
                'rank': self._simulate_rank(),
                'impressions': self._simulate_impressions(),
                'clicks': self._simulate_clicks(),
                'conversions': self._simulate_conversions(),
                'ctr': self._simulate_ctr(),
                'acos': self._simulate_acos()
            }
        except Exception as e:
            print(f"Error getting keyword performance: {str(e)}")
            return {}

    def _simulate_rank(self):
        """Simulate keyword rank (1-100)."""
        import random
        return random.randint(1, 100)

    def _simulate_impressions(self):
        """Simulate impressions (100-10000)."""
        import random
        return random.randint(100, 10000)

    def _simulate_clicks(self):
        """Simulate clicks (10-1000)."""
        import random
        return random.randint(10, 1000)

    def _simulate_conversions(self):
        """Simulate conversions (1-100)."""
        import random
        return random.randint(1, 100)

    def _simulate_ctr(self):
        """Simulate CTR (0.01-0.1)."""
        import random
        return random.uniform(0.01, 0.1)

    def _simulate_acos(self):
        """Simulate ACOS (0.1-0.4)."""
        import random
        return random.uniform(0.1, 0.4) 