# Food Reviews

## Overview

+ With food information from Open Food Facts
+ With purchasing history and user reviews from Amazon Reviews
+ Explore the change in purchasing behavior throughout the years
+ Explore difference in user's buying behaviors

## Dataset

### Open Food Facts

+ Summary:
  + Public dataset collected by volunteers on Food Facts
  + i.e. information on product packages
  + With 175 attributes, most have high NA counts except main nutrients
  + 950 thousand entries
+ Attributes:
  + [Full list of attributes](https://static.openfoodfacts.org/data/data-fields.txt)
+ Resources:
  + [Open Food Facts](https://world.openfoodfacts.org/)
  + [Open Food Facts data](https://world.openfoodfacts.org/data)

### Amazon Reviews: Grocery

+ Summary:
  + Amazon Customer Reviews, on grocery category
  + From year 2000 to 2015
  + Including comments and ratings on each product by each customer
  + 2.4 million entries
+ Attributes:
  + [Full List of attributes](https://s3.amazonaws.com/amazon-reviews-pds/tsv/index.txt)
+ Resources:
  + [Amazon Customer Reviews Dataset](https://registry.opendata.aws/amazon-reviews/)
  + [Documentation](https://s3.amazonaws.com/amazon-reviews-pds/readme.html)
  + [Amazon Reviews, Grocery Dataset](https://s3.amazonaws.com/amazon-reviews-pds/tsv/amazon_reviews_us_Grocery_v1_00.tsv.gz)

### Merged data

+ Merge both dataset by Product Name/Title
  + tokenize and normalize the names/titles
  + remove duplications
  + merge food facts with each customer reviews

## Exploratory Analysis

+ What is the change in energy consumption by each month?
  + ![nutrients-energy](./figures/nutrients-energy.png)
+ Does higher sugar content equal to higher product rating?
  + ![sugar](./figures/sugar.png)
+ ...

## Modelling

+ 