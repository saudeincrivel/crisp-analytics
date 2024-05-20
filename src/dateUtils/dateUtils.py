from datetime import datetime


def convert_to_iso(date_str: str) -> str:
    date_obj = datetime.strptime(date_str, "%d/%m/%Y")
    return date_obj.isoformat() + 'Z'


# date_str = "22/12/2023"
# iso_date_str = convert_to_iso(date_str)
# print(iso_date_str)  # Output: "2023-12-22T00:00:00Z"
