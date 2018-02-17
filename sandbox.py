import datetime
from models import *

def loadCategoryChart():
    today = datetime.date.today()
    last_month = today.replace(day=1) - datetime.timedelta(days=1)
    print(last_month.strftime("%m"))


loadCategoryChart()