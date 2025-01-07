from datetime import datetime

def format_date(value: str) -> str:
    # Parse the string into a datetime object (assuming ISO format like '2024-11-15T00:00:00+00:00')
    dt = datetime.fromisoformat(value)
    # Return the formatted string (e.g., '15/11/2024')
    return dt.strftime('%d/%m/%Y')

def lowerName(value:str) -> str:
    return value.replace(' ','').lower()

def blanks(value) -> str:
    if value==None:
        return ''
    return value

def chkType(value) -> str:
    return type(value)