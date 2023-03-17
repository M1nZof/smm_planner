import gspread

from gspread import utils
from pathlib import Path
from datetime import datetime

GOOGLE_CREDENTIALS = gspread.service_account(Path.joinpath(Path.cwd(), 'service_account.json').__str__())
SPREADSHEET = GOOGLE_CREDENTIALS.open('smm-planer-table')
WORKSHEET = SPREADSHEET.sheet1
BLACK = {'red': 0.0, 'green': 0.0, 'blue': 0.0}
WHITE = {'red': 1.0, 'green': 1.0, 'blue': 1.0}
GREEN = {'red': 0.0, 'green': 1.0, 'blue': 0.0}
RED = {'red': 1.0, 'green': 0.0, 'blue': 0.0}


def format_date(str_date):
    date_ = datetime.strptime(str_date, "%d.%m.%Y").date()
    return date_, date_.strftime("%Y-%m-%d"), date_.strftime("%Y/%m/%d")


def format_time(str_time):
    time_ = datetime.strptime(str_time, "%H:%M").time()
    return time_, time_.strftime("%H:%M")


def format_date_and_time_to_datetime(date, time):
    return datetime(date.year, date.month, date.day, time.hour, time.minute, time.second)


def get_date_and_time(post):
    return post['date'], post['time']


def get_formatted_datetime(post):
    date_, time_ = get_date_and_time(post)
    formatted_date = format_date(date_)
    formatted_time = format_time(time_)
    formatted_datetime = format_date_and_time_to_datetime(formatted_date[0], formatted_time[0])
    return formatted_datetime


def get_datetime_now():
    datetime_now = datetime.now()
    return datetime(datetime_now.year, datetime_now.month, datetime_now.day, datetime_now.hour,
                    datetime_now.minute)


def get_all_new_posts():
    all_posts = WORKSHEET.get_all_records()
    all_new_posts = []
    for post in all_posts:
        if not post['public_fact'] or post['duration']:
            for key, value in post.items():
                if value == '':
                    post[key] = None
            all_new_posts.append(post)
    return all_new_posts


def get_all_records():
    all_records = WORKSHEET.get_all_records()
    return all_records


def get_all_times():
    for time in sorted(WORKSHEET.col_values(4)):
        if '-' not in time:
            continue
        time_, time_chr = format_time(time)
        print(time_, time_chr)


def get_posts_count():
    return len(WORKSHEET.col_values(1)) - 1


def post_cell_text(row, col, text=''):
    WORKSHEET.update_cell(row, col, text)
    pass


def format_cell(row, col, b_color, f_color):
    WORKSHEET.format(utils.rowcol_to_a1(row, col), {
        "backgroundColor": b_color,
        "textFormat": {
            "foregroundColor": f_color,
        }
    })
