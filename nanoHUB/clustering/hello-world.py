# import os
# from pathlib import Path
# import pandas as pd
# from pandas.core.frame import DataFrame
# from dataclasses import dataclass

from datetime import datetime, timezone


print('Hello World')
# print(datetime.now(timezone.utc).astimezone().tzinfo)
print(f"current time: {datetime.now().strftime('%H:%M:%S')}")