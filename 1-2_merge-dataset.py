#!/usr/bin/env python
# coding: utf-8
import os
import re
import numpy as np
import pandas as pd

# stop words list
from nltk.corpus import stopwords
stopWords = set(stopwords.words('english'))

# disable SettingWithCopyWarning 
pd.options.mode.chained_assignment = None # default='warn'


# ## Open Food Facts dataset
# 

# In[2]:


# set dtype of code to keep values starting with 0
# set dtype of others to avoid DtypeWarning
data_path = 'D:\DATA\practice-dataset\zipped'
off = pd.read_csv(os.path.join(data_path, 'en.openfoodfacts.org.products.csv.zip'),                   dtype={'code': 'object', 
                         'emb_codes': 'object', 'emb_codes_tags': 'object',
                         'first_packaging_code_geo': 'object',
                         'cities_tags': 'object', 'additives': 'object',
                         'ingredients_from_palm_oil_tags': 'object'}, \
                  compression='zip', sep='\t')
off.shape


# In[31]:


# drop columns not needed for cross-analysis with reviews
dropped_cols = ['creator', 'created_t', 'created_datetime',                  'last_modified_t', 'last_modified_datetime',                  'generic_name', 'packaging', 'packaging_tags',                  'origins', 'origins_tags',                  'manufacturing_places', 'manufacturing_places_tags',                  'labels', 'emb_codes', 'emb_codes_tags',                  'first_packaging_code_geo', 'cities', 'cities_tags',                  'purchase_places', 'stores', 'countries',                  'ingredients_text', 'traces']
# 'categories',


# In[32]:


# drop columns not used for product review
off.drop(dropped_cols, axis=1, inplace=True)
# filter out url columns (columns names containing 'url')
off = off.filter(regex=r'^((?!url).)*$', axis=1)
off.shape


# In[33]:


# drop the rows without Product Name
off = off[off.product_name.notna()].reset_index(drop=True)
off.shape


# In[37]:


off.columns.values


# In[ ]:





# ### Open Food Facts subset

# #### Take product of "Jif" for example

# In[6]:


# product of Jif
jif = off[off.product_name.str.match(r'^(JIF|Jif|jif)\s.*')]
jif.product_name.head()


# In[7]:


jif.drop('categories', axis=1, inplace=True)
# jif.product_name = jif.product_name.str.lower() # lowercase when extracting tokens
jif.reset_index(drop=True, inplace=True)
jif.shape


# In[ ]:





# #### Take product of "Cheetos" for example

# In[8]:


# Product of Cheetos
cheetos = off[off.product_name.str.match(r'^(Cheetos|CHEETOS|cheetos)\s.*')]
cheetos.drop('categories', axis=1, inplace=True)

# cheetos.product_name = cheetos.product_name.str.lower() 
cheetos.reset_index(drop=True, inplace=True)
cheetos.shape


# In[ ]:





# In[ ]:





# ## Amazon Reviews: Grocery dataset
# + https://registry.opendata.aws/amazon-reviews/
# + https://s3.amazonaws.com/amazon-reviews-pds/readme.html
# + http://jmcauley.ucsd.edu/data/amazon/

# In[3]:


data_path = 'D:\DATA\practice-dataset\gzipped'
amz = pd.read_csv(os.path.join(data_path, 'amazon_reviews_us_Grocery_v1_00.tsv.gz'),                   dtype={'customer_id': 'object', 'product_parent': 'object',                          'star_rating': 'object', 
                         'helpful_votes': pd.Int64Dtype(), 'total_votes': pd.Int64Dtype()}, \
                  compression='gzip', sep='\t', \
                  error_bad_lines=False, warn_bad_lines=False)
# pd.Int64Dtype() allows NaN
amz.drop(['marketplace', 'product_category', 'product_id'], axis=1, inplace=True)
# row 1841896 contains date as star_rating
amz.drop(1841896, axis=0, inplace=True)
amz.shape


# In[4]:


amz[amz.product_parent == '795563511'].product_title.unique()


# In[ ]:





# In[ ]:





# ### Amazon Review subset

# #### Take product of "jif" for example

# In[20]:


# Jif product reviews
jif_rev = amz[amz.product_title.str.match(r'^(JIF|Jif|jif)\s.*')]
# jif_rev.product_title = jif_rev.product_title.str.lower()
jif_rev.reset_index(drop=True, inplace=True)
jif_rev.shape


# In[21]:


jif_rev.product_title.unique()[:10]


# In[ ]:





# #### Take product of "cheetos" for example

# In[22]:


# cheetos
che_rev = amz[amz.product_title.str.match(r'^(Cheetos|cheetos|CHEETOS)\s.*')]
# che_rev.product_title = che_rev.product_title.str.lower()
che_rev.reset_index(drop=True, inplace=True)
che_rev.shape


# In[23]:


che_rev.product_title.unique()[:10]


# In[ ]:





# In[ ]:





# In[ ]:





# ### Get mapping from `product_parent` code
# + key: product_parent
# + value: product title/name
# + how?
#   + group by product_parent and product_title, count the occurance of another column
#     + getting multi-index with product_parent and product_title, with only columnt of count
#   + `reset_index` on the multi-index dataframe, get regular data frame
#   + method1:
#     + sort by count values, from large to small; drop duplicates on product_parent
#     + get the unique product_parent code for each product_title
#   + method2:
#     + get index by 
#       + group by prodcut_parent and transform each row to the group's max value
#       + compare with group max value, the boolean array is the index
#     + get the unique pair by boolean slicing on array

# In[24]:


# group by product_parent and product_title, get count of each title under a code
# there could be multiple titles under the same code
tmp = amz.loc[:, ['product_title', 'product_parent', 'customer_id']]        .groupby(['product_parent', 'product_title']).count().reset_index()
tmp.shape


# In[25]:


tmp.product_parent.unique().shape


# In[26]:


tmp.sort_values(by='customer_id', ascending=False).head()


# In[27]:


tmp.sort_values('customer_id', ascending=False).drop_duplicates('product_parent').shape


# In[15]:


# method 1
mapping = tmp.sort_values('customer_id', ascending=False).drop_duplicates('product_parent')
# mapping.shape
mapping = mapping.sort_values('product_parent').drop('customer_id', axis=1).reset_index(drop=True)
mapping.head()

# method 2, there're still some duplicated product_parent
idx = tmp.groupby('product_parent')['customer_id'].transform(max) == tmp['customer_id']
mapping = tmp[idx]
mapping.shape
# mapping2.product_parent.values.shape, len(set(mapping2.product_parent.values))# export the mapping
data_path = 'D:\DATA\OurFoods'
mapping.to_csv(os.path.join(data_path, 'mapping.csv'), 
               index=False)
# In[ ]:





# In[ ]:





# In[ ]:





# ## Tokenize Product Name/Title
# + Regex for processing names/titles
#   + lowercasing
#   + remove non-word but not white space, b.c, special symbols when naming
#   + remove digit and values after it, b.c. values after digits are packaging size
#   + remove space, i.e. empty string, in list
#   + remove stopwords, e.g. 'by', 'the'...etc
# + **Problem with Regex**
#   + many product names/titles starting with digit
#     + causing too many empty tuples

# In[16]:


jif.shape, jif_rev.shape, cheetos.shape, che_rev.shape


# In[17]:


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

jif.product_name.apply(lambda s: tuple(filter(None, re.sub(r'[^\w\s]|(\d.*$)', '', s).split(' '))))
jif_rev.product_title.apply(lambda s: tuple(filter(None, re.sub(r'[^\w\s]|(\d.*$)', '', s).split(' '))))
jif.shape, jif_rev.shape
# In[18]:


jif['tokens'] = jif.product_name.apply(pname_tokenize)
jif_rev['tokens'] = jif_rev.product_title.apply(pname_tokenize)
jif.shape, jif_rev.shape


# In[19]:


cheetos['tokens'] = cheetos.product_name.apply(pname_tokenize)
che_rev['tokens'] = che_rev.product_title.apply(pname_tokenize)
cheetos.shape, che_rev.shape


# In[ ]:





# In[20]:


# adding tokens to mapping
mapping['tokens'] = mapping.product_title.apply(pname_tokenize)
mapping.head()


# In[ ]:





# In[ ]:





# ## Dataset Merge (keep cateogory and main nutrients)
# + AMZ dataset
#   + merge with mapping on unique id, to add tokens to amz
# + OFF dataset
#   + tokenize the product name
#   + use mapping to find unique id for the token
# + Merge
#   + merge both on unique id (product parent)

# In[ ]:





# ### Prepare `amz`
# + using mapping dataset
# + merget `amz` with mapping to get `tokens` attribute
# + some `tokens` are empty, drop by empty tuple

# In[21]:


# merge amz with mapping
amz = amz.merge(mapping[['product_parent', 'tokens']], how='left', on='product_parent')
amz.shape


# In[22]:


# drop empty tuples, for now
amz = amz[amz.tokens != tuple()]
amz.shape


# In[ ]:





# ### Prepare `off`
# + problems:
#   + same product, having different pacakge size, is on different row
#   + i.e. same tokens, but having multiple entries
# + either select one of the entries, or taking avearage on all entries
# + 

# In[23]:


off.shape


# In[24]:


# only taking categories and main nutrients
sub = off.loc[:, ['product_name', 'categories_tags', 'main_category_en',                   'energy_100g', 'fat_100g', 'fiber_100g', 'carbohydrates_100g',                   'proteins_100g', 'salt_100g', 'sodium_100g', 'sugars_100g']]
sub.sort_values(['product_name', 'main_category_en', 'categories_tags'],                 inplace=True, na_position='last')
sub.reset_index(drop=True, inplace=True)
sub.shape


# In[25]:


sub.main_category_en.notna().sum()


# In[ ]:





# In[26]:


func = {'categories_tags':'last', 'main_category_en':'last',         'energy_100g':'mean', 'fat_100g':'mean', 'fiber_100g':'mean',         'carbohydrates_100g':'mean', 'proteins_100g':'mean',         'salt_100g':'mean', 'sodium_100g':'mean', 'sugars_100g':'mean'}
# take first on strings and mean on numbers with duplicate product names
sub = sub.groupby('product_name', as_index=False).agg(func)        .assign(tokens=lambda d: d.product_name.apply(pname_tokenize))
# handle the same with ducplicated tokens
sub = sub[sub.tokens != tuple()].reset_index(drop=True)    .groupby('tokens', as_index=False).agg(func)
# remove rows without energy data
sub = sub[sub.energy_100g.notna()]

sub.head()


# In[27]:


sub.main_category_en.notna().sum()


# In[ ]:





# In[ ]:





# In[ ]:





# ### Merge and Output both dataset
# + need to process the main category, having different language inputs
#   + remove non-english inputs
#   + or, replace with english categories

# In[28]:


df = amz.merge(sub, how='inner', on='tokens')
df.shape


# In[29]:


data_path = 'D:\DATA\OurFoods'
df.to_csv(os.path.join(data_path, 'merged_amz-off_3.csv.gz'),          compression='gzip', index=False)


# In[ ]:





# In[47]:


# get the value counts and outputs as dataframe
d = df.main_category_en.value_counts()        .rename_axis('unique_values')        .reset_index(name='counts')
# get the row that is not in English
d[d.unique_values.str.contains(':')].head()


# In[46]:


# the category is due to wrong token
# use these products to redesign the tokneization method
df[df.main_category_en == 'fr:the-vert-aromatise'].iloc[:3, [3, 10, 12, 13, 14]]


# In[ ]:





# In[ ]:




# clean main_category labels before exporting data
non_eng = []
eng = []
for s in df.main_category_en.unique():
    if type(s) == str:
        if ':' ian s: non_eng.append(s)
        else: eng.append(s)
eng
# In[ ]:





# ### Inspect other nutrients
# + Can more nutrients be included in the output dataset?
# + IF enough data, after merging

# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# ## Dataset Merge
# + AMZ dataset
#   + merge with mapping on unique id, to add tokens to amz
# + OFF dataset
#   + tokenize the product name
#     + but product name may be duplicated, with same token
#     + group by the token, extract only the rows of product name with max counts
#   + use mapping to find unique id for the token
# + Merge
#   + merge both on unique id (product parent)

# In[26]:


off.shape, amz.shape, mapping.shape


# ### Prepare `amz`
# + using mapping dataset
# + merget `amz` with mapping to get `tokens` attribute
# + some `tokens` are empty, drop by empty tuple

# In[27]:


# merge amz with mapping
amz = amz.merge(mapping[['product_parent', 'tokens']], how='left', on='product_parent')
amz.shape


# In[28]:


# drop empty tuples, for now
amz = amz[amz.tokens != tuple()]
amz.shape


# In[ ]:





# ### Prepare `off`
# + problems:
#   + same product, having different pacakge size, is on different row
#   + i.e. same tokens, but having multiple entries
# + either select one of the entries, or taking avearage on all entries
# + 

# In[29]:


off.shape


# In[30]:


# take mean on duplicate product names
temp = off.groupby('product_name', as_index=False).mean()    .assign(tokens=lambda d: d.product_name.apply(pname_tokenize))
# take mean on duplicated tokens
temp = temp[temp.tokens != tuple()].reset_index(drop=True)    .groupby('tokens', as_index=False).mean()
# remove rows without energy data
temp = temp[temp.energy_100g.notna()]


# In[31]:


temp.tokens.value_counts()
# duplicate tokens


# In[32]:


temp.shape


# In[ ]:





# ### Merge and Output both dataset

# In[48]:


df = amz.merge(temp, how='inner', on='tokens')
df.shape


# In[ ]:





# In[ ]:




data_path = 'D:\DATA\OurFoods'
df.to_csv(os.path.join(data_path, 'merged_amz-off_2.csv.gz'),\
          compression='gzip', index=False)
# In[ ]:




