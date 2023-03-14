import gspread
from pathlib import Path


def main():
    filename = str(Path.joinpath(Path.cwd(), 'service_account.json'))
    gc = gspread.service_account(filename=filename)
    sh = gc.open('smm-planer-table')

    print(sh.sheet1.get('A1'))


if __name__ == '__main__':
    main()
