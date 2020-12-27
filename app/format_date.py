def get_formatted_date(timestamp):
    """ 
    Formats a timestamp into a human readable string. 
    <Day><ordinal> <Month>, <Year>
    eg.. 1st January, 2020
    """

    day = timestamp.strftime('%d')
    # default ordinal for date.
    ordinal = 'th'
    # Check number and change default ordinal
    if day[len(day)-1] == '1':
        ordinal = 'st'
    elif day[len(day)-1] == '2':
        ordinal = 'nd'
    elif day[len(day)-1] == '3':
        ordinal = 'rd'

    try:
        return timestamp.strftime(f'%d{ordinal} %b, %Y')
    except ValueError:
        return "Value out of range"
