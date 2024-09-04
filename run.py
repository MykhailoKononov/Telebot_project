import telebot
import os

from dotenv import  load_dotenv
from telebot import types
from app.calc import (revenue_per_day, avg_revenue_per_order_daily,
                      previous_day_revenue, previous_day_avg_revenue_per_order,
                      revenue_per_month, avg_revenue_per_order_monthly,
                      previous_month_revenue, previous_month_avg_revenue_per_order,
                      arpu_daily, arpu_monthly,
                      previous_arpu_daily, previous_arpu_monthly,
                      revenue_plot, revenue_by_item_plot, pie_plot_category,
                      annual_revenue, boxplot, plot_arpu_aov)

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.config import config

bot = telebot.TeleBot(config.TOKEN)

def markup_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Today', callback_data='today'))
    markup.add(types.InlineKeyboardButton('Select exact date', callback_data='select_exact_date'))
    markup.add(types.InlineKeyboardButton('Select month', callback_data='select_month'))
    markup.add(types.InlineKeyboardButton('Annual report', callback_data='annual_report'))
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     'Hi, dude!👋\n\nI can send you some metrics and graphics and other smart \
stuff🙂\n\nJust select the date and check this out',
                     reply_markup=markup_keyboard())


@bot.callback_query_handler(func=lambda call: call.data in ['today', 'select_exact_date', 'select_month', 'annual_report'])
def choose_type(call):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)

    if call.data == 'today':
        bot.send_message(call.message.chat.id, 'There is still no data about today\'s sales, try again later or \
choose another date', reply_markup=markup_keyboard())

    elif call.data == 'select_exact_date':
        msg = bot.send_message(call.message.chat.id, 'Please enter the date in the format <em>yyyy-mm-dd</em>:',
                               parse_mode='html')
        bot.register_next_step_handler(msg, get_date)

    elif call.data == 'select_month':
        msg = bot.send_message(call.message.chat.id, 'Please enter the month in the format <em>yyyy-mm</em>:',
                               parse_mode='html')
        bot.register_next_step_handler(msg, get_month)

    elif call.data == 'annual_report':
        bot.send_message(call.message.chat.id, 'Here are your annual reports below:',
                               parse_mode='html')


        plot_path = annual_revenue(call.message.chat.id)
        if plot_path:
            with open(plot_path, 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo)
            os.remove(plot_path)


        arpu_aov_plot_path = plot_arpu_aov(call.message.chat.id)
        if arpu_aov_plot_path:
            with open(arpu_aov_plot_path, 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo)
            os.remove(arpu_aov_plot_path)


        box_plot_path = boxplot(call.message.chat.id)
        if box_plot_path:
            with open(box_plot_path, 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo)
            os.remove(box_plot_path)


def get_date(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    given_date = message.text
    try:
        parsed_date = given_date

        revenue = float(revenue_per_day(parsed_date))
        previous_revenue = float(previous_day_revenue(parsed_date))
        avg_per_order = float(avg_revenue_per_order_daily(parsed_date))
        previous_avg_per_order = float(previous_day_avg_revenue_per_order(parsed_date))
        arpu = float(arpu_daily(parsed_date))
        previous_arpu = float(previous_arpu_daily(parsed_date))


        if revenue == 0:
            bot.send_message(message.chat.id,
                             f'No revenue data available for <em>{parsed_date}</em>. \n\nPlease choose another date and \
make sure that you want to know statistics of <u><em>2023rd year</em></u>😉', parse_mode='html')
            bot.register_next_step_handler(message, get_date)
            return

        if previous_revenue > 0:
            percent_diff = ((revenue - previous_revenue) / previous_revenue) * 100
            percent_diff_str = f" ({'+' if percent_diff > 0 else ''}{percent_diff:.2f}%) {'📈' if percent_diff > 0 else '📉'}"
        else:
            percent_diff_str = " (No previous day data available)"

        if previous_avg_per_order > 0:
            avg_percent_diff = ((avg_per_order - previous_avg_per_order) / previous_avg_per_order) * 100
            avg_percent_diff_str = f" ({'+' if avg_percent_diff > 0 else ''}{avg_percent_diff:.2f}%) {'📈' if avg_percent_diff > 0 else '📉'}"
        else:
            avg_percent_diff_str = " (No previous day data available)"

        if previous_arpu > 0:
            arpu_percent_diff = ((arpu - previous_arpu) / previous_arpu) * 100
            arpu_percent_diff_str = f" ({'+' if arpu_percent_diff > 0 else ''}{arpu_percent_diff:.2f}%) {'📈' if arpu_percent_diff > 0 else '📉'}"
        else:
            arpu_percent_diff_str = " (No previous day data available)"

        bot.send_message(message.chat.id, f'Here is your statistics for <em>{parsed_date}</em>:\n\n\
Total revenue: {round(revenue, 2)}$ {percent_diff_str}\n\
Average revenue per order: {round(avg_per_order, 2)}$ {avg_percent_diff_str}\n\
ARPU: {round(arpu, 2)}$ {arpu_percent_diff_str}', parse_mode='html', reply_markup=markup_keyboard())
        bot.register_next_step_handler(message, choose_type)

    except ValueError:
        message_back = bot.send_message(message.chat.id,
                         'Invalid format🫠\nPlease enter the date in the format <em>yyyy-mm-dd</em>',
                         parse_mode='html')
        bot.register_next_step_handler(message_back, get_date)
def get_month(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    given_month = message.text

    try:
        # Parsing entered date
        parsed_month = given_month

        # Calcs
        revenue_monthly = float(revenue_per_month(parsed_month))
        previous_revenue_monthly = float(previous_month_revenue(parsed_month))
        avg_per_order_monthly = float(avg_revenue_per_order_monthly(parsed_month))
        previous_avg_per_order_monthly = float(previous_month_avg_revenue_per_order(parsed_month))
        arpu_month = float(arpu_monthly(parsed_month))
        previous_arpu_month = float(previous_arpu_monthly(parsed_month))

        # Checking data availability
        if revenue_monthly is None or revenue_monthly == 0 or arpu_month == 0:
            bot.send_message(message.chat.id,
                             f'No revenue data available for <em>{parsed_month}</em>. \n\nPlease choose another\
 month and make sure that you want to know statistics of <u><em>2023rd year</em></u>😉', parse_mode='html')
            bot.register_next_step_handler(message, get_month)
            return

        # Checking and calculating perc diff for revenue monthly
        if previous_revenue_monthly > 0:
            percent_diff = ((revenue_monthly - previous_revenue_monthly) / previous_revenue_monthly) * 100
            percent_diff_str = f" ({'+' if percent_diff > 0 else ''}{percent_diff:.2f}%) {'📈' if percent_diff > 0 else '📉'}"
        else:
            percent_diff_str = " (No previous month data available)"

        # Checking and calculating perc diff for avg revenue monthly
        if previous_avg_per_order_monthly > 0:
            avg_percent_diff = ((avg_per_order_monthly - previous_avg_per_order_monthly) / previous_avg_per_order_monthly) * 100
            avg_percent_diff_str = f" ({'+' if avg_percent_diff > 0 else ''}{avg_percent_diff:.2f}%) {'📈' if avg_percent_diff > 0 else '📉'}"
        else:
            avg_percent_diff_str = " (No previous month data available)"

        if previous_arpu_month > 0:
            arpu_percent_diff = ((arpu_month - previous_arpu_month) / previous_arpu_month) * 100
            arpu_percent_diff_str = f" ({'+' if arpu_percent_diff > 0 else ''}{arpu_percent_diff:.2f}%) {'📈' if arpu_percent_diff > 0 else '📉'}"
        else:
            arpu_percent_diff_str = " (No previous month data available)"

        markup = InlineKeyboardMarkup()

        markup.add(InlineKeyboardButton("Revenue Distribution", callback_data=f"revenue_plot_{parsed_month}"))

        markup.add(InlineKeyboardButton("Distribution by item", callback_data=f"item_plot_{parsed_month}"))

        markup.add(InlineKeyboardButton("Distribution by category", callback_data=f"category_plot_{parsed_month}"))

        markup.add(InlineKeyboardButton("Back", callback_data="back_to_keyboard"))


        # Message sending
        bot.send_message(message.chat.id, f'Here is your statistics for <em>{parsed_month}</em>:\n\n\
Total revenue: {round(revenue_monthly, 2)}$ {percent_diff_str}\n\
Average revenue per order: {round(avg_per_order_monthly, 2)}$ {avg_percent_diff_str}\n\
ARPU: {round(arpu_month, 2)}$ {arpu_percent_diff_str}', parse_mode='html', reply_markup=markup)

    except ValueError:
        bot.send_message(message.chat.id, 'Invalid format🫠\nPlease enter the month in the format <em>yyyy-mm</em>',
                         parse_mode='html')
        bot.register_next_step_handler(message, get_month)


@bot.callback_query_handler(func=lambda call: call.data.startswith('revenue_plot_') or call.data.startswith(
    'item_plot_') or call.data.startswith('category_plot_') or call.data == 'back_to_keyboard')
def send_plot(call):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    # Extract the month from callback_data
    selected_month = call.data.split('_')[-1]

    if "revenue_plot" in call.data:
        plot_path = revenue_plot(call.message.chat.id, selected_month)

        if plot_path:
            with open(plot_path, 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo)
            os.remove(plot_path)
        else:
            bot.send_message(call.message.chat.id, f'No revenue plot available for {selected_month}.')

    elif "item_plot" in call.data:
        item_plot_path = revenue_by_item_plot(call.message.chat.id, selected_month)

        if item_plot_path:
            with open(item_plot_path, 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo)
            os.remove(item_plot_path)
        else:
            bot.send_message(call.message.chat.id, f'No item distribution chart available for {selected_month}.')

    elif "category_plot" in call.data:
        category_plot_path = pie_plot_category(call.message.chat.id, selected_month)

        if category_plot_path:
            with open(category_plot_path, 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo)
            os.remove(category_plot_path)
        else:
            bot.send_message(call.message.chat.id, f'No category distribution chart available for {selected_month}.')

    elif call.data == "back_to_keyboard":

        bot.send_message(call.message.chat.id, 'Choose the type of report on keyboard', reply_markup=markup_keyboard())

    bot.answer_callback_query(call.id)  # Acknowledge the callback query


bot.polling(none_stop=True)