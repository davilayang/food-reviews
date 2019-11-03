#!/usr/bin/env python
# coding: utf-8

# Merge Datasets: AMZ and OFF
import os
import re
import numpy as np
import pandas as pd

# use english stop words list
from nltk.corpus import stopwords
stopWords = set(stopwords.words('english'))

# disable SettingWithCopyWarning 
pd.options.mode.chained_assignment = None # default='warn'


# Open Food Facts dataset
# set dtype of code to keep values starting with 0, set dtype of others to avoid DtypeWarning
data_path = 'D:\DATA\practice-dataset\zipped'
off = pd.read_csv(os.path.join(data_path, 'en.openfoodfacts.org.products.csv.zip'),                   dtype={'code': 'object', 
                         'emb_codes': 'object', 'emb_codes_tags': 'object',
                         'first_packaging_code_geo': 'object',
                         'cities_tags': 'object', 'additives': 'object',
                         'ingredients_from_palm_oil_tags': 'object'}, \
                  compression='zip', sep='\t')

# Handle OFF: unnecessary attributes
# drop attributes not related not related to reviews analyses
dropped_cols = ['creator', 'created_t', 'created_datetime',                  'last_modified_t', 'last_modified_datetime',                  'generic_name', 'packaging', 'packaging_tags',                  'origins', 'origins_tags',                  'manufacturing_places', 'manufacturing_places_tags',                  'labels', 'emb_codes', 'emb_codes_tags',                  'first_packaging_code_geo', 'cities', 'cities_tags',                  'purchase_places', 'stores', 'countries',                  'ingredients_text', 'traces']
# drop columns not used for product review
off.drop(dropped_cols, axis=1, inplace=True)
# filter out url columns (columns names containing 'url')
off = off.filter(regex=r'^((?!url).)*$', axis=1)
# drop the rows without Product Name
off = off[off.product_name.notna()].reset_index(drop=True)


# Amazon Reviews: Grocery dataset
data_path = 'D:\DATA\practice-dataset\gzipped'
amz = pd.read_csv(os.path.join(data_path, 'amazon_reviews_us_Grocery_v1_00.tsv.gz'),                   dtype={'customer_id': 'object', 'product_parent': 'object',                          'star_rating': 'object', 
                         'helpful_votes': pd.Int64Dtype(), 'total_votes': pd.Int64Dtype()}, \
                  compression='gzip', sep='\t', \
                  error_bad_lines=False, warn_bad_lines=False)
# pd.Int64Dtype() allows NaN
amz.drop(['marketplace', 'product_category', 'product_id'], axis=1, inplace=True)
# row 1841896 contains date as star_rating
amz.drop(1841896, axis=0, inplace=True)


# Handle AMZ: multiple product_name in a product_parent 
# group by product_parent and product_title, get count of each title under a code
# there could be multiple titles under the same code
tmp = amz.loc[:, ['product_title', 'product_parent', 'customer_id']]        .groupby(['product_parent', 'product_title']).count().reset_index()
mapping = tmp.sort_values('customer_id', ascending=False).drop_duplicates('product_parent')
mapping = mapping.sort_values('product_parent').drop('customer_id', axis=1).reset_index(drop=True)


# Tokenize Product Name/Title
def pname_tokenize(string):
    """
    Given product name/title string, processes and outputs tuple of tokens
    """
    # lower and remove non-word except spaces
    r = re.sub(r'[^\w\s]', '', string.lower())
    # remove digits and any string after it
    r = re.sub(r'\d.*$', '', r)
    # remove empty string and stopwords, then return tuple
    return tuple(sorted(set(filter(None, r.split(' '))) - set(stopWords)))

# adding tokens to mapping dataframe
mapping['tokens'] = mapping.product_title.apply(pname_tokenize)

# Dataset Merge 

# Prepare `amz`
# merge amz with mapping
amz = amz.merge(mapping[['product_parent', 'tokens']], how='left', on='product_parent')
# drop empty tuples, for now
amz = amz[amz.tokens != tuple()]

# Prepare `off`
# only taking categories and main nutrients
sub = off.loc[:, ['product_name', 'categories_tags', 'main_category_en',                   'energy_100g', 'fat_100g', 'fiber_100g', 'carbohydrates_100g',                   'proteins_100g', 'salt_100g', 'sodium_100g', 'sugars_100g']]
sub.sort_values(['product_name', 'main_category_en', 'categories_tags'],                 inplace=True, na_position='last')
sub.reset_index(drop=True, inplace=True)

# aggregate function for each attribute
func = {'categories_tags':'last', 'main_category_en':'last',         'energy_100g':'mean', 'fat_100g':'mean', 'fiber_100g':'mean',         'carbohydrates_100g':'mean', 'proteins_100g':'mean',         'salt_100g':'mean', 'sodium_100g':'mean', 'sugars_100g':'mean'}
# for duplicated product_name: 
# 1. take first value on strings attribute
# 2. take mean on numeric attrbutes
sub = sub.groupby('product_name', as_index=False).agg(func)        .assign(tokens=lambda d: d.product_name.apply(pname_tokenize))
# for duplicated tokens
# use the same aggregate function as before
sub = sub[sub.tokens != tuple()].reset_index(drop=True)    .groupby('tokens', as_index=False).agg(func)
# remove rows without energy data
sub = sub[sub.energy_100g.notna()]


# Merge and Output both dataset
df = amz.merge(sub, how='inner', on='tokens')
df.shape

# export as csv file
data_path = 'D:\DATA\OurFoods'
df.to_csv(os.path.join(data_path, 'merged_amz-off_3.csv.gz'),\
          compression='gzip', index=False)


# export to database
# ```python
# import os
# from sqlalchemy import create_engine
# from sqlalchemy import types
# 
# from dotenv import load_dotenv # env variables
# load_dotenv(verbose=True)
# 
# SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
# engine = create_engine(SQLALCHEMY_DATABASE_URI)
# 
# df.to_sql(name="food_reviews", con=engine, if_exists='replace',
#                schema='public', index=True)
# ```
