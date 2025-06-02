# Amazon Sales Suite

A comprehensive dashboard for Amazon sellers to track sales, manage inventory, and analyze performance using the Amazon Selling Partner API.

## Features

- 📊 Interactive Dashboard with sales trends and metrics
- 📦 Product management and tracking
- 📈 Detailed sales reports and analytics
- 📱 Mobile-responsive design
- 🔄 Real-time data synchronization with Amazon

## Prerequisites

Before you begin, ensure you have:
1. Python 3.8 or higher installed
2. An Amazon Seller account
3. Amazon Selling Partner API credentials

### Required Amazon Credentials
You'll need the following from your Amazon Seller account:
- Refresh Token
- Client ID
- Client Secret
- AWS Access Key
- AWS Secret Key
- Role ARN
- Marketplace ID

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/salessuite.git
   cd salessuite
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   Create a file named `.env` in the project root with the following content:
   ```
   SECRET_KEY=your-secret-key
   AMAZON_REFRESH_TOKEN=your-refresh-token
   AMAZON_CLIENT_ID=your-client-id
   AMAZON_CLIENT_SECRET=your-client-secret
   AMAZON_AWS_ACCESS_KEY=your-aws-access-key
   AMAZON_AWS_SECRET_KEY=your-aws-secret-key
   AMAZON_ROLE_ARN=your-role-arn
   AMAZON_MARKETPLACE_ID=your-marketplace-id
   ```

6. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

## Running the Application

1. **Start the application**
   ```bash
   flask run
   ```

2. **Access the dashboard**
   Open your web browser and go to:
   ```
   http://localhost:5000
   ```

## Using the Dashboard

### Dashboard Overview
The main dashboard provides:
- Total number of products
- Total sales count
- 30-day revenue
- Sales trends
- Top performing products

### Products Section
1. Click "Products" in the navigation bar
2. View all your products in a table format
3. Use the search bar to find specific products
4. Click the eye icon to view detailed product information
5. Click the chart icon to view product-specific reports

### Reports Section
1. Click "Reports" in the navigation bar
2. Create new reports:
   - Click "New Report"
   - Select report type (Sales, Orders, or Inventory)
   - Choose date range
   - Click "Create Report"
3. View existing reports:
   - Use filters to find specific reports
   - Click the eye icon to view report details
   - Click the download icon to export reports
   - Click the trash icon to delete reports

## Common Tasks

### Creating a Sales Report
1. Go to the Reports page
2. Click "New Report"
3. Fill in the form:
   - Name: "Monthly Sales Report"
   - Type: "Sales"
   - Start Date: Choose start date
   - End Date: Choose end date
4. Click "Create Report"

### Viewing Product Performance
1. Go to the Products page
2. Find your product using the search bar
3. Click the eye icon to view:
   - Total sales
   - Revenue
   - Sales history

### Exporting Data
1. Go to the Reports page
2. Find the report you want to export
3. Click the download icon
4. Choose your preferred format

## Troubleshooting

### Common Issues

1. **Application won't start**
   - Check if the virtual environment is activated
   - Verify all dependencies are installed
   - Ensure the `.env` file exists with correct credentials

2. **No data showing**
   - Verify Amazon API credentials
   - Check internet connection
   - Ensure you have active listings on Amazon

3. **Database errors**
   - Run `flask db upgrade` to ensure database is up to date
   - Check if the database file exists

### Getting Help

If you encounter any issues:
1. Check the error message in the terminal
2. Verify your Amazon API credentials
3. Ensure all environment variables are set correctly

## Security Notes

- Never share your `.env` file
- Keep your Amazon API credentials secure
- Regularly update your dependencies
- Use strong passwords for any authentication

## Support

For additional help:
1. Check the documentation
2. Review the Amazon Selling Partner API documentation
3. Contact support with specific error messages

## License

This project is licensed under the MIT License - see the LICENSE file for details.
