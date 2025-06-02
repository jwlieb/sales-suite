# Amazon Sales Suite

A comprehensive analytics and reporting platform for Amazon sellers, built with Flask and the Amazon Selling Partner API.

## Features

### Dashboard
- Overview of total products, sales, and revenue
- Sales trends visualization
- Top performing products list

### Product Management
- List and search products
- View detailed product information
- Track product performance metrics
- Advanced analytics for each product:
  - Competitor price tracking and analysis
  - Profit margin calculations and trends
  - Keyword performance monitoring

### Analytics
#### Competitor Analysis
- Market position visualization
- Price history tracking
- Price change alerts
- Competitor offer monitoring

#### Profit Analysis
- Profit margin trends
- Cost breakdown visualization
- Performance metrics
- Revenue analysis

#### Keyword Performance
- Keyword ranking trends
- Top performing keywords
- Keyword health metrics
- Optimization opportunities
- CTR and ACOS tracking

### Reports
- Generate and manage various report types:
  - Sales reports
  - Order reports
  - Inventory reports
- Download reports in multiple formats
- Schedule automated report generation

## Prerequisites

- Python 3.8 or higher
- Amazon Seller Account
- Amazon Selling Partner API credentials:
  - Client ID
  - Client Secret
  - Refresh Token
  - AWS Access Key
  - AWS Secret Key
  - Role ARN
  - Marketplace ID

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/amazon-sales-suite.git
cd amazon-sales-suite
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db

# Amazon SP-API Credentials
AMAZON_CLIENT_ID=your-client-id
AMAZON_CLIENT_SECRET=your-client-secret
AMAZON_REFRESH_TOKEN=your-refresh-token
AMAZON_AWS_ACCESS_KEY=your-aws-access-key
AMAZON_AWS_SECRET_KEY=your-aws-secret-key
AMAZON_ROLE_ARN=your-role-arn
AMAZON_MARKETPLACE_ID=your-marketplace-id
```

5. Initialize the database:
```bash
flask db upgrade
```

## Usage

1. Start the development server:
```bash
flask run
```

2. Access the application at `http://localhost:5000`

### Key Features Usage

#### Product Analytics
1. Navigate to the Products page
2. Click the "Analytics" button next to any product
3. View detailed analytics in three main sections:
   - Competitors: Track market position and price changes
   - Profit Analysis: Monitor margins and costs
   - Keywords: Analyze search performance

#### Reports
1. Go to the Reports page
2. Click "Create Report"
3. Select report type and date range
4. Generate and download reports

## API Endpoints

### Products
- `GET /api/products/<asin>` - Get product details
- `GET /api/products/<product_id>/competitors` - Get competitor analysis
- `GET /api/products/<product_id>/profit` - Get profit analysis
- `GET /api/products/<product_id>/keywords` - Get keyword analysis
- `POST /api/products/<product_id>/track` - Start tracking product metrics

### Reports
- `GET /api/reports` - List all reports
- `POST /api/reports` - Create new report
- `GET /api/reports/<report_id>` - Get report details
- `DELETE /api/reports/<report_id>` - Delete report

### Sales
- `GET /api/sales` - Get sales data with date range filter

## Development

### Project Structure
```
amazon-sales-suite/
├── app/
│   ├── models/         # Database models
│   ├── routes/         # API and view routes
│   ├── services/       # Business logic and API services
│   ├── templates/      # HTML templates
│   └── static/         # CSS, JS, and other static files
├── migrations/         # Database migrations
├── tests/             # Test files
├── .env               # Environment variables
├── config.py          # Configuration
├── requirements.txt   # Dependencies
└── run.py            # Application entry point
```

### Running Tests
```bash
python -m pytest
```

### Database Migrations
```bash
flask db migrate -m "Migration message"
flask db upgrade
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security

- Never commit sensitive credentials to version control
- Keep your `.env` file secure and out of version control
- Regularly rotate your Amazon SP-API credentials
- Monitor API usage and set up alerts for unusual activity

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Roadmap

- [ ] Enhanced competitor analysis with market share tracking
- [ ] Advanced keyword research and optimization suggestions
- [ ] Automated price optimization
- [ ] Inventory forecasting
- [ ] Custom report builder
- [ ] Email notifications for important alerts
- [ ] Mobile app for monitoring on the go
