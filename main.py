import gspread
from pathlib import Path


def main():
    gc = gspread.service_account(Path.joinpath(Path.cwd(), 'service_account.json').__str__())
    sh = gc.open('smm-planer-table')

    print(sh.sheet1.get('A1'))


if __name__ == '__main__':
    main()
