# -*- coding: utf-8 -*-
"""An elsapy module that contains decorators and other utilities to make the
project more maintainable.
"""

import pandas as pd
from . import log_util

logger = log_util.get_logger(__name__)


def recast_df(df):
    
    int_resp_fields = [
            'document-count',
            'citedby-count',
            ]
    date_resp_fields = [
            'prism:coverDate',
            ]
    if 'link' in df.columns:
        df['link'] = df.link.apply(
            lambda x: dict([(e['@rel'], e['@href']) for e in x]))
    for int_field in int_resp_fields:
        if int_field in df.columns:
            df[int_field] = df[int_field].apply(
                    int)
    for date_field in date_resp_fields:
        if date_field in df.columns:
            print("Converting {}".format(date_field))
            df[date_field] = df[date_field].apply(
                    pd.Timestamp)
    return df