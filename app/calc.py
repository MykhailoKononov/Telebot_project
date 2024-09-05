from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from app.config import config

import pandas as pd
import psycopg2
import psycopg2.extras
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import logging
matplotlib.use('Agg')
logging.basicConfig(level=logging.INFO)


# Func that connects to Postgres Database
def get_data_sqldb(query):
    conn = psycopg2.connect(
        f"dbname={config.DB_NAME} user={config.USER} host={config.HOST} password={config.PASSWORD} port={config.PORT}")
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query)
    rows = cur.fetchall()
    data = []

    for row in rows:
        data.append(dict(row))
    return pd.DataFrame(data)


# Queries to overwrite data from database to variables _df
orders_df = get_data_sqldb("""select* from orders""")
categories_df = get_data_sqldb("""select* from categories""")
items_df = get_data_sqldb("""select* from items""")
customers_df = get_data_sqldb('''select* from customers''')

# Joining dataframes into one, dropping not needed columns
orders_customers = pd.merge(orders_df, customers_df, on='customer_id')
orders_customers_items = pd.merge(orders_customers, items_df, on='item_id', suffixes=('_orders', '_items'))
merged_df = pd.merge(orders_customers_items, categories_df, on='category_id', suffixes=('_orders', '_categories'))
df = merged_df.drop(['item_id', 'first_name', 'last_name', 'description_orders',
                     'category_id', 'description_categories'], axis=1)
# Adding new column year_month and overwriting date columns into str
df['date'] = pd.to_datetime(df['date'])
df['year_month'] = df['date'].dt.strftime('%Y-%m')
df['date'] = df['date'].dt.strftime('%Y-%m-%d')


# DAILY METRICS
# 2 next funcs calculate total revenue and percent difference for daily option
def revenue_per_day(date):
    revenue = df['revenue'][df['date'] == date].sum()
    return revenue


def previous_day_revenue(date):
    date_dt = datetime.strptime(date, '%Y-%m-%d')
    previous_date = date_dt - timedelta(days=1)
    previous_date_str = previous_date.strftime('%Y-%m-%d')
    return revenue_per_day(previous_date_str)


# 2 next funcs calculate AOV (average order value) and percent difference for daily option
def avg_revenue_per_order_daily(date):

    revenue_sum = df['revenue'][df['date'] == date].sum()
    order_count = df['order_id'][df['date'] == date].count()

    if order_count > 0:
        result = revenue_sum / order_count
    else:
        result = 0

    return result


def previous_day_avg_revenue_per_order(date):
    date_dt = datetime.strptime(date, '%Y-%m-%d')
    previous_date = date_dt - timedelta(days=1)
    previous_date_str = previous_date.strftime('%Y-%m-%d')
    return avg_revenue_per_order_daily(previous_date_str)


# 2 next funcs calculate ARPU (average revenue per user/customer) and percent difference for daily option
def arpu_daily(date):

    revenue_sum = df['revenue'][df['date'] == date].sum()
    unique_customers = df[df['date'] == date]['customer_id'].nunique()

    if unique_customers > 0:
        result = revenue_sum / unique_customers
    else:
        result = 0

    return result


def previous_arpu_daily(date):
    date_dt = datetime.strptime(date, '%Y-%m-%d')
    previous_date = date_dt - timedelta(days=1)
    previous_date_str = previous_date.strftime('%Y-%m-%d')
    return arpu_daily(previous_date_str)


# MONTHLY METRICS
# 2 next funcs calculate total revenue and percent difference for monthly option
def revenue_per_month(year_month):
    revenue_monthly = df['revenue'][df['year_month'] == year_month].sum()
    return revenue_monthly


def previous_month_revenue(year_month):
    year_month_dt = datetime.strptime(year_month, '%Y-%m')
    previous_month = year_month_dt - relativedelta(months=1)
    previous_month_str = previous_month.strftime('%Y-%m')
    return revenue_per_month(previous_month_str)


# 2 next funcs calculate AOV and percent difference for monthly option
def avg_revenue_per_order_monthly(year_month):
    revenue_sum = df['revenue'][df['year_month'] == year_month].sum()
    order_count = df['order_id'][df['year_month'] == year_month].count()
    if order_count > 0:
        result = revenue_sum / order_count
    else:
        result = 0

    return result


def previous_month_avg_revenue_per_order(year_month):
    year_month_dt = datetime.strptime(year_month, '%Y-%m')
    previous_month = year_month_dt - relativedelta(months=1)
    previous_month_str = previous_month.strftime('%Y-%m')
    return avg_revenue_per_order_monthly(previous_month_str)


# 2 next funcs calculate ARPU and percent difference for monthly option
def arpu_monthly(year_month):
    revenue_sum = df['revenue'][df['year_month'] == year_month].sum()
    unique_customers = df[df['year_month'] == year_month]['customer_id'].nunique()

    if unique_customers > 0:
        result = revenue_sum / unique_customers
    else:
        result = 0

    return result


def previous_arpu_monthly(year_month):
    year_month_dt = datetime.strptime(year_month, '%Y-%m')
    previous_month = year_month_dt - relativedelta(months=1)
    previous_month_str = previous_month.strftime('%Y-%m')
    return arpu_monthly(previous_month_str)


# 1st graphic for 'Select month' Inline Keyboard Button (Revenue Distribution)
def revenue_plot(chat_id, year_month):
    df['date'] = pd.to_datetime(df['date'])
    df_filtered = df[df['year_month'] == year_month]

    if df_filtered.empty:
        result = f"No data available for {year_month}."
        return result

    plt.figure(figsize=(12, 6))
    sns.barplot(x=df_filtered['date'].dt.day, y=df_filtered['revenue'], hue=df_filtered['date'].dt.day,
                palette="viridis", legend=False)

    plt.title(f'Revenue Distribution for {year_month}', fontsize=16)
    plt.xlabel('Day of the Month', fontsize=14)
    plt.ylabel('Revenue', fontsize=14)
    plt.xticks(rotation=45)
    plt.grid(True)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')

    image_path = f'revenue_distribution_{year_month}_{chat_id}.png'
    plt.savefig(image_path, bbox_inches='tight')
    plt.close()

    return image_path


# 2nd graphic for 'Select month' Inline Keyboard Button (Distribution by item)
def revenue_by_item_plot(chat_id, year_month):
    df_filtered = df[df['year_month'] == year_month]

    if df_filtered.empty:
        result = f"No data available for {year_month}."
        return result

    plt.figure(figsize=(12, 6))
    sns.barplot(x=df_filtered['item_name'], y=df_filtered['revenue'], hue=df_filtered['item_name'],
                palette="viridis", legend=False)

    plt.title(f'Revenue Distribution by Items for {year_month}', fontsize=16)
    plt.xlabel('Item\'s name', fontsize=14)
    plt.ylabel('Revenue', fontsize=14)
    plt.xticks(rotation=45)
    plt.grid(True)

    # Saving plot with unique name
    image_path = f'revenue_distribution_by_item_{year_month}_{chat_id}.png'
    plt.savefig(image_path, bbox_inches='tight')
    plt.close()

    return image_path


# 3rd graphic for 'Select month' Inline Keyboard Button (Distribution by category)
def pie_plot_category(chat_id, year_month):

    df_filtered = df[df['year_month'] == year_month]

    if df_filtered.empty:
        result = f"No data available for {year_month}."
        return result

    revenue_by_item = df_filtered.groupby('category_name')['revenue'].sum()

    plt.figure(figsize=(12, 6))
    plt.pie(revenue_by_item, labels=revenue_by_item.index, autopct='%1.1f%%',
            colors=sns.color_palette('viridis', len(revenue_by_item)))

    plt.title(f'Revenue Distribution by Category for {year_month}', fontsize=16)

    # Saving plot with unique name
    image_path = f'revenue_distribution_by_category{year_month}_{chat_id}.png'
    plt.savefig(image_path, bbox_inches='tight')
    plt.close()

    return image_path


# 1st graphic for 'Annual report' Main Inline Keyboard Button
def annual_revenue(chat_id):
    df['year_month'] = pd.Categorical(df['year_month'], categories=sorted(df['year_month'].unique()), ordered=True)

    df['rolling_revenue'] = df['revenue'].rolling(10).mean()

    plt.figure(figsize=(12, 6))

    sns.barplot(x=df['year_month'], y=df['revenue'], palette="viridis", capsize=0.15)
    sns.lineplot(x=df['year_month'], y=df['rolling_revenue'], color="red", label="Rolling Average", marker="o")

    plt.title(f'Monthly Revenue Distribution for 2023 with rolling mean(10)', fontsize=16)
    plt.xlabel('Month', fontsize=14)
    plt.ylabel('Revenue', fontsize=14)
    plt.xticks(rotation=45)
    plt.grid(True)

    # Saving plot with unique name
    image_path = f'annual_rolling_plot_{chat_id}.png'
    plt.savefig(image_path, bbox_inches='tight')
    plt.close()

    return image_path


# 2nd graphic for 'Annual report' Main Inline Keyboard Button
def boxplot(chat_id):
    df['year_month'] = pd.to_datetime(df['year_month'])

    monthly_revenue = df.groupby(['item_name', 'year_month'])['order_id'].count().reset_index()

    plt.figure(figsize=(20, 6))
    sns.boxplot(x='item_name', y='order_id', data=monthly_revenue, hue='item_name', palette='viridis')

    plt.title('Monthly revenue spread for each item', fontsize=16)
    plt.xlabel('Item\'s name', fontsize=14)
    plt.ylabel('Monthly number of orders', fontsize=14)
    plt.xticks(fontsize=14, rotation=45)
    plt.yticks(fontsize=14)
    plt.grid(True)
    df['year_month'] = df['year_month'].dt.strftime('%Y-%m')

    # Saving plot with unique name
    image_path = f'annual_box_plot_{chat_id}.png'
    plt.savefig(image_path, bbox_inches='tight')
    plt.close()

    return image_path


# 3rd graphic for 'Annual report' Main Inline Keyboard Button
def plot_arpu_aov(chat_id):

    df['year_month'] = pd.to_datetime(df['year_month'])

    monthly_metrics = df.groupby('year_month').agg(
        revenue=('revenue', 'sum'),
        orders=('order_id', 'nunique'),
        customers=('customer_id', 'nunique')
    ).reset_index()

    monthly_metrics['arpu'] = monthly_metrics['revenue'] / monthly_metrics['customers']
    monthly_metrics['aov'] = monthly_metrics['revenue'] / monthly_metrics['orders']

    fig, axes = plt.subplots(1, 2, figsize=(20, 6))

    sns.barplot(x='year_month', y='arpu', data=monthly_metrics, ax=axes[0], palette='Blues_d')
    axes[0].set_title('Monthly ARPU', fontsize=16)
    axes[0].set_xlabel('Month', fontsize=14)
    axes[0].set_ylabel('ARPU', fontsize=14)
    axes[0].tick_params(axis='x', rotation=45, labelsize=12)
    axes[0].tick_params(axis='y', labelsize=12)
    axes[0].grid(True)

    sns.barplot(x='year_month', y='aov', data=monthly_metrics, ax=axes[1], palette='Greens_d')
    axes[1].set_title('Monthly AOV', fontsize=16)
    axes[1].set_xlabel('Month', fontsize=14)
    axes[1].set_ylabel('AOV', fontsize=14)
    axes[1].tick_params(axis='x', rotation=45, labelsize=12)
    axes[1].tick_params(axis='y', labelsize=12)
    axes[1].grid(True)
    df['year_month'] = df['year_month'].dt.strftime('%Y-%m')

    # Saving plot with unique name
    image_path = f'arpu_aov_plot_{chat_id}.png'
    plt.savefig(image_path, bbox_inches='tight')
    plt.close()

    return image_path
