import gspread

gc = gspread.service_account()

sh = gc.open('smm-planer-table')

print(sh.sheet1.get('A1'))