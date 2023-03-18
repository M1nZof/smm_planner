import gspread

from gspread import utils
from pathlib import Path
from datetime import datetime

GOOGLE_CREDENTIALS = gspread.service_account(Path.joinpath(Path.cwd().parent, 'ENV', 'service_account.json').__str__())
SPREADSHEET = GOOGLE_CREDENTIALS.open('smm-planer-table')
WORKSHEET = SPREADSHEET.sheet1
BLACK = {'red': 0.0, 'green': 0.0, 'blue': 0.0}
WHITE = {'red': 1.0, 'green': 1.0, 'blue': 1.0}
GREEN = {'red': 0.0, 'green': 1.0, 'blue': 0.0}
RED = {'red': 1.0, 'green': 0.0, 'blue': 0.0}


def format_date(str_date):
    if '-' in str_date:
        date_ = datetime.strptime(str_date, "%d-%m-%Y").date()
    if '.' in str_date:
        date_ = datetime.strptime(str_date, "%d.%m.%Y").date()
    else:
        print('Неверно введена дата ')
        return False
    return date_, date_.strftime("%Y-%m-%d"), date_.strftime("%Y/%m/%d")


def format_time(str_time):
    if '-' in str_time:
        time_ = datetime.strptime(str_time, "%H-%M").time()
    elif ':' in str_time:
        time_ = datetime.strptime(str_time, "%H:%M").time()
    else:
        print('Неверно введено время ')
        return False
    return time_, time_.strftime("%H:%M")


def get_formatted_datetime(post_date, post_time):
    date_ = format_date(post_date)[0]
    time_ = format_time(post_time)[0]
    formatted_datetime = datetime(date_.year, date_.month, date_.day, time_.hour, time_.minute, time_.second)
    return formatted_datetime


def get_datetime_now():
    datetime_now = datetime.now()
    return datetime(datetime_now.year, datetime_now.month, datetime_now.day, datetime_now.hour,
                    datetime_now.minute)


def get_all_new_posts():
    all_posts = WORKSHEET.get_all_records()
    all_new_posts = []
    for num, post in enumerate(all_posts):
        print(num, post['Telegram'], post['Telegram_rez'])
        if (post['link_google_document'] and (post['Telegram'] == 'TRUE' and not post['Telegram_rez'])):
            print(num, 'Телега не опубликована')
        if post['link_google_document'] and ((post['Telegram'] == 'TRUE' and not post['Telegram_rez']) or (post['VK'] == 'TRUE' and not post['VK_rez'])\
                or (post['OK'] == 'TRUE' and not post['OK_rez'])):
            all_new_posts.append(post)
        elif not post['link_google_document']:
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
