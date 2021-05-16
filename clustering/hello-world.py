print ("Hello World")

from pprint import pprint
items = [1, 2, 3]
pprint(items)

# from DateTime import DateTime
#
# x = DateTime('1997/3/9 1:45pm')
# print(x.parts())

import os

def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))

# print(list_files("."))
# print(os.listdir(".")) # returns list
# print(os.listdir(".")) # returns list
# print(os.listdir("/")) # returns list
# print(os.listdir("/app")) # returns list



import pandas
import numpy as np
pandas.Series([1, 3, 5, np.nan, 6, 8])


# import numpy
# pandas.Series([1, 3, 5, numpy.nan, 6, 8])



