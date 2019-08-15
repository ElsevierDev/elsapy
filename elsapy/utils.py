# -*- coding: utf-8 -*-
"""An elsapy module that contains decorators and other utilities to make the
project more maintainable.
"""

import pandas as pd
from . import log_util

logger = log_util.get_logger(__name__)


def recast_df(df):
    '''Recasts a data frame so that it has proper date fields and a more 
    useful data structure for URLs'''
    int_resp_fields = [
            'document-count',
            'citedby-count',
            ]
    date_resp_fields = [
            'prism:coverDate',
            ]
    
    # Modify data structure for storing links/URLs in a DF
    if 'link' in df.columns:
        if '@rel' in df.link[0][0].keys():
            # To deal with inconsistency. In some API responses, the link type 
            #   field uses '@rel' as key; in others, it uses '@ref'.
            link_type_key ='@rel'
        else:
            link_type_key = '@ref'
        df['link'] = df.link.apply(
            lambda x: dict([(e[link_type_key], e['@href']) for e in x]))
    # Recast fields that contain integers from strings to the integer type
    for int_field in int_resp_fields:
        if int_field in df.columns:
            df[int_field] = df[int_field].apply(
                    int)
    # Recast fields that contain datetime from strings to a datetime type
    for date_field in date_resp_fields:
        if date_field in df.columns:
            logger.info("Converting {}".format(date_field))
            df[date_field] = df[date_field].apply(
                    pd.Timestamp)
    return df