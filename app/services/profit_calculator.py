from datetime import datetime
from app import db
from app.models import Product, ProfitMargin, Sale
from app.services.amazon_sp_api import AmazonSPAPIService

class ProfitCalculator:
    def __init__(self, sp_api_service: AmazonSPAPIService):
        self.sp_api = sp_api_service

    def calculate_profit_margin(self, product: Product, date: datetime = None):
        """Calculate profit margin for a product on a specific date."""
        if date is None:
            date = datetime.utcnow().date()

        try:
            # Get product details from Amazon
            product_details = self.sp_api.get_product_details(product.asin)
            
            # Get sales data for the date
            sales = Sale.query.filter(
                Sale.product_id == product.id,
                Sale.date == date
            ).all()

            # Calculate total revenue
            total_revenue = sum(sale.revenue for sale in sales)
            
            # Get Amazon fees
            amazon_fees = self._calculate_amazon_fees(product_details, sales)
            
            # Get shipping costs
            shipping_cost = self._calculate_shipping_cost(product_details, sales)
            
            # Get product cost
            product_cost = self._get_product_cost(product)
            
            # Get storage fees
            storage_fees = self._calculate_storage_fees(product_details)
            
            # Get advertising costs
            advertising_cost = self._get_advertising_cost(product, date)
            
            # Get returns cost
            returns_cost = self._calculate_returns_cost(product, date)
            
            # Calculate net profit
            total_costs = (
                amazon_fees +
                shipping_cost +
                product_cost +
                storage_fees +
                advertising_cost +
                returns_cost
            )
            
            net_profit = total_revenue - total_costs
            margin_percentage = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

            # Create profit margin record
            profit_margin = ProfitMargin(
                product_id=product.id,
                date=date,
                selling_price=product_details.get('price', 0),
                amazon_fees=amazon_fees,
                shipping_cost=shipping_cost,
                product_cost=product_cost,
                storage_fees=storage_fees,
                advertising_cost=advertising_cost,
                returns_cost=returns_cost,
                net_profit=net_profit,
                margin_percentage=margin_percentage
            )

            db.session.add(profit_margin)
            db.session.commit()

            return profit_margin

        except Exception as e:
            db.session.rollback()
            print(f"Error calculating profit margin: {str(e)}")
            return None

    def _calculate_amazon_fees(self, product_details, sales):
        """Calculate Amazon fees including referral and FBA fees."""
        # This would need to be implemented based on Amazon's fee structure
        # For now, using a simplified calculation
        total_units = sum(sale.quantity for sale in sales)
        referral_fee = product_details.get('price', 0) * 0.15  # 15% referral fee
        fba_fee = 3.31  # Example FBA fee per unit
        return (referral_fee + fba_fee) * total_units

    def _calculate_shipping_cost(self, product_details, sales):
        """Calculate shipping costs."""
        # This would need to be implemented based on your shipping costs
        # For now, using a simplified calculation
        total_units = sum(sale.quantity for sale in sales)
        return total_units * 2.50  # Example shipping cost per unit

    def _get_product_cost(self, product):
        """Get the cost of the product."""
        # This would need to be implemented based on your product costs
        # For now, returning a placeholder
        return 0.0

    def _calculate_storage_fees(self, product_details):
        """Calculate Amazon storage fees."""
        # This would need to be implemented based on Amazon's storage fee structure
        # For now, using a simplified calculation
        return 0.0

    def _get_advertising_cost(self, product, date):
        """Get advertising costs for the product."""
        # This would need to be implemented based on your advertising data
        # For now, returning a placeholder
        return 0.0

    def _calculate_returns_cost(self, product, date):
        """Calculate costs associated with returns."""
        # This would need to be implemented based on your returns data
        # For now, returning a placeholder
        return 0.0

    def get_profit_trends(self, product_id: int, days: int = 30):
        """Get profit margin trends over time."""
        return ProfitMargin.query.filter(
            ProfitMargin.product_id == product_id
        ).order_by(
            ProfitMargin.date.desc()
        ).limit(days).all()

    def get_product_performance(self, product_id: int):
        """Get overall product performance metrics."""
        margins = ProfitMargin.query.filter(
            ProfitMargin.product_id == product_id
        ).all()

        if not margins:
            return None

        return {
            'average_margin': sum(m.margin_percentage for m in margins) / len(margins),
            'highest_margin': max(m.margin_percentage for m in margins),
            'lowest_margin': min(m.margin_percentage for m in margins),
            'total_profit': sum(m.net_profit for m in margins),
            'average_profit': sum(m.net_profit for m in margins) / len(margins)
        } 