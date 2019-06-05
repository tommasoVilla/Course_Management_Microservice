import datetime


def is_valid_date(date_string):
    if "-" not in date_string:
        return False
    if len(date_string.split("-")) != 3:
        return False
    if not date_string.split("-")[0].isnumeric() \
            or not date_string.split("-")[1].isnumeric() \
            or not date_string.split("-")[2].isnumeric():
        return False
    if not int(date_string.split("-")[0]) in range(1, 32):
        return False
    if not int(date_string.split("-")[1]) in range(1, 13):
        return False
    if not int(date_string.split("-")[2]) in range(datetime.datetime.now().year, datetime.datetime.now().year + 10):
        return False
    return True


def is_valid_year(year_string):
    if "-" not in year_string:
        return False
    if not len(year_string.split("-")) == 2:
        return False
    if not year_string.split("-")[0].isnumeric() or not year_string.split("-")[1].isnumeric():
        return False
    if not int(year_string.split("-")[0]) in range(datetime.datetime.now().year - 1, datetime.datetime.now().year + 10):
        return False
    if not int(year_string.split("-")[1]) in range(datetime.datetime.now().year - 1, datetime.datetime.now().year + 10):
        return False
    if int(year_string.split("-")[1]) - int(year_string.split("-")[0]) != 1:
        return False
    return True


def is_valid_schedule(schedule):
    if len(schedule) <= 0:
        return False

    for elem in schedule:
        if 'day' not in elem or not elem['day'].isalpha():
            return False
        if 'startTime' not in elem or not is_valid_time(elem['startTime']):
            return False
        if 'endTime' not in elem or not is_valid_time(elem['endTime']):
            return False
        if not is_valid_time_range(elem['startTime'], elem['endTime']):
            return False
        if 'room' not in elem or not trim(elem['room']).isalnum():
            return False
    return True


def is_valid_time_range(start, end):
    if int(start.split(":")[0]) > int(end.split(":")[0]):
        return False
    elif int(start.split(":")[0]) == int(end.split(":")[0]):
        if int(start.split(":")[1]) >= int(end.split(":")[1]):
            return False
    return True


def is_valid_time(time_string):
    if ":" not in time_string:
        return False
    if len(time_string.split(":")) != 2:
        return False
    if not time_string.split(":")[0].isnumeric() or not time_string.split(":")[1].isnumeric():
        return False
    if not int(time_string.split(":")[0]) in range(0, 24):
        return False
    if not int(time_string.split(":")[1]) in range(0, 60):
        return False
    return True


def trim(string):
    return string.replace(" ", "").replace("\t", "").replace("\n", "")
