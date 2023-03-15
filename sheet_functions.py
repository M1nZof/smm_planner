import gspread
from pathlib import Path
from datetime import datetime


GOOGLE_CREDENTIALS = gspread.service_account(Path.joinpath(Path.cwd(), 'service_account.json').__str__())
SPREADSHEET = GOOGLE_CREDENTIALS.open('smm-planer-table')
WORKSHEET = SPREADSHEET.sheet1


def main():
    # print(get_all_posts())
    # get_posts_count()
    get_all_records()


def format_date(str_date):
    date_ = datetime.strptime(str_date, "%d.%m.%Y").date()
    return date_, date_.strftime("%Y-%m-%d"), date_.strftime("%Y/%m/%d")


def format_time(str_time):
    time_ = datetime.strptime(str_time, "%H-%M").time()
    return time_, time_.strftime("%H:%M")


def get_all_posts():
    all_values = WORKSHEET.get_all_values()
    all_posts = []
    for post in all_values[1:]:
        all_posts.append(dict(zip(all_values[0], post)))
    return all_posts


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
    posts_count = len(WORKSHEET.col_values(1)) - 1
    print(posts_count)


def post_cell_text(col, row, text=''):
    pass


if __name__ == '__main__':
    main()
