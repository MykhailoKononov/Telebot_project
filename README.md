# Revenue Analysis and Reporting Bot

This project is a Python-based bot that connects to a PostgreSQL database, performs revenue-related data analysis, and generates various revenue-related visualizations. The bot is integrated with Telegram, allowing users to interact with it and receive reports and charts for daily, monthly, and annual revenue metrics.

---

## Features

- **Data Collection**: The bot fetches data from PostgreSQL and joins multiple tables (orders, categories, items, customers) into one dataset.
- **Revenue Metrics**: The bot calculates various metrics such as:
  - **Revenue per Day**: Total revenue generated on a specific day.
  - **Average Order Value (AOV)**: Average revenue per order.
  - **Average Revenue per User (ARPU)**: Average revenue generated per unique customer.
  - **Revenue Distribution**: Bar and pie charts showing revenue distribution by date, item, and category.
- **Visualization**: The bot generates plots using `seaborn` and `matplotlib`, including:
  - Daily and monthly revenue distribution.
  - Revenue distribution by item and category.
  - Rolling average of monthly revenue.
  - ARPU and AOV comparisons across months.

---

## Requirements

- Python 3.8+
- PostgreSQL
- Libraries:
  - `pandas`
  - `psycopg2`
  - `seaborn`
  - `matplotlib`
  - `python-dotenv`
  - `pydantic-settings`
  - `telegram`

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/MykhailoKononov/Telebot_project.git
   cd Telebot_project
   ```

2. **Set up environment variables**:
   Create a `.env` file in the root directory of the project and add your PostgreSQL and Telegram credentials:
   ```bash
   TOKEN=your_telegram_bot_token
   DB_NAME=your_database_name
   USER=your_database_user
   HOST=your_database_host
   PASSWORD=your_database_password
   PORT=your_database_port
   ```

3. **Run the bot**:
   Start the bot by running the following command:
   ```bash
   python run.py
   ```

---

## Usage

The bot allows you to request various reports and visualizations by interacting with inline keyboard buttons in Telegram. The following options are available:

- **Select Month**:
  - View revenue distribution by day, item, or category.
  - Generate revenue reports for a specific month.

- **Annual Report**:
  - View monthly revenue distribution with a rolling average.
  - Generate a box plot of monthly order counts for each item.
  - Compare ARPU and AOV for each month.

Simply interact with the bot to choose the desired report, and it will generate the corresponding chart and send it to you in the chat.

## Example Output

- **Revenue Distribution by Day**: A bar chart showing daily revenue distribution for a specific month.
- **Revenue Distribution by Item**: A bar chart showing revenue distribution by item for a specific month.
- **Revenue Distribution by Category**: A pie chart showing the share of revenue per category for a specific month.
- **Monthly Revenue with Rolling Average**: A bar chart showing monthly revenue and its rolling average for the year.
- **Box Plot of Monthly Orders**: A box plot visualizing the spread of monthly orders for each item.

## Contributing

Feel free to fork the repository, make improvements, or submit pull requests. Contributions are welcome!

---

This README should help anyone interested in your project understand what it does, how to set it up, and how to use it. If you have any specific details or changes you'd like to add, let me know!
