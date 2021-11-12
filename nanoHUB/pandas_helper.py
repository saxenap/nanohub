import pandas as pd
from IPython.display import display, Markdown


def get_rows_by_keyvalue(df: pd.DataFrame, key_name: str, search_value) -> pd.DataFrame:
    return df.loc[df[key_name] == search_value]


def get_number_of_rows(df: pd.DataFrame) -> int:
    return len(df.index)


def display_number_of_rows(df: pd.DataFrame) -> None:
    display(Markdown("**A total of %d entries pulled in**" % get_number_of_rows(df)))