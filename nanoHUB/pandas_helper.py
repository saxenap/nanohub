import pandas as pd
import numpy as np
from IPython.display import display, Markdown


def get_rows_by_keyvalue(df: pd.DataFrame, key_name: str, search_value) -> pd.DataFrame:
    return df.loc[df[key_name] == search_value]


def get_number_of_rows(df: pd.DataFrame) -> int:
    return len(df.index)


def display_number_of_rows(df: pd.DataFrame) -> None:
    display(Markdown("**A total of %d entries pulled in**" % get_number_of_rows(df)))


def remove_display_restrictions(pd: pd) -> None:
    pd.set_option('display.max_columns', None)  # or 1000
    pd.set_option('display.max_rows', None)  # or 1000
    pd.set_option('display.max_colwidth', None)  # or 199


def compare_dfs(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:

    ne_stacked = (df1 != df2).stack()
    changed = ne_stacked[ne_stacked]
    changed.index.names = ['id', 'col']

    difference_locations = np.where(df1 != df2)
    changed_from = df1.values[difference_locations]
    changed_to = df2.values[difference_locations]

    return pd.DataFrame({'from': changed_from, 'to': changed_to}, index=changed.index)