import pandas
from IPython.display import display, Markdown


def get_rows_by_keyvalue(df: pandas.DataFrame, key_name: str, search_value) -> pandas.DataFrame:
    return df.loc[df[key_name] == search_value]


def get_number_of_rows(df: pandas.DataFrame) -> int:
    return len(df.index)


def display_number_of_rows(df: pandas.DataFrame) -> None:
    display(Markdown("**A total of %d entries pulled in**" % get_number_of_rows(df)))