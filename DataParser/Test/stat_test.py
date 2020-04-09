"""
Title: stat_test.py
By: M5DS1
    Purpose:

"""
# Note: ignore the squiggly lines if using pycharm

import json
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")


# from src.plot_utils import *
# from ..src.stat_utils import message_decoder
from DataParser.src.stat_utils import message_decoder

message_decoder("00",'../Includes/v1.0/')
