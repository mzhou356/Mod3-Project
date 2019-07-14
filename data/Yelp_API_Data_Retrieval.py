#!/usr/bin/env python
# coding: utf-8

# In[209]:


# Scraping Data From Yelp for restaurants in DC


# In[210]:


# import libraries
import pandas as pd
import numpy as np
import requests
import time  # set sleep time
import os  # import yelpkey
import pickle  # save as a pickle file


# In[4]:


# stored yelpkey as a global environment
api_key = os.environ.get('YELPKEY')


# In[211]:


# due to 1000 offset limit on regular business search call on yelp
# have to use category to get all business id information
# set headers to enter api key
headers = {
    'Authorization': 'Bearer {}'.format(api_key)
}
url_c = 'https://api.yelp.com/v3/categories'  # endpoint for categories
# set location to united states (closest to DC)
url_params_c = {'locale': 'en_US',
                }
response_c = requests.get(url_c, headers=headers, params=url_params_c)
# check for status of response
# print(response_c)
# print(type(response_c.text))
# print(response_c.text[:1000])


# In[46]:


# find all categories for business as restaurants in United States
categories = [c['alias'] for c in response_c.json()['categories']
              if 'restaurants' in c['parent_aliases']]


# In[140]:


# save categories as a list for future usage (just in case)
with open('categories.pkl', 'wb') as f:
    pickle.dump(categories, f)


# In[65]:


# create a yelp_call for business search end points
# we want to have business detail end points but we need to use
# business search to get businessid for the url call


def yelp_call(url_params, api_key):
    '''
    url_params: will update based upon categories of food 
    return: all restaurants from DC location as a list of restaurants
    '''
    url = 'https://api.yelp.com/v3/businesses/search'
    # headers for api_key
    headers = {
        'Authorization': 'Bearer {}'.format(api_key)
    }
    response = requests.get(url, headers=headers, params=url_params)
    return response


# In[68]:


# create an empty list for all businesses
# collect the first 50 calls for each categories
# use the reponse for each category to get num of total restaurants for each category
# get more calls for num above 50 and check to make sure non has over 1000 restaurants
Businesses = []
location = 'DC'
# num of restaurants for each categories dictionary
num_per_cat = {}
for cat in categories:
    url_params = {'categories': cat,
                  'location': location.replace(' ', '+'),
                  'limit': 50
                  }
    result = yelp_call(url_params, api_key).json()
    # in case give key error, then create an empty list
    Businesses.extend(result.get('businesses', []))
    # in case give key error, then give value of 0
    num_per_cat[cat] = result.get('total', 0)


# In[143]:


# save num_per_cat dict as pickle file for future usage
# and prevent wasting more api calls
with open('num_per_cat.pkl', 'wb') as f:
    pickle.dump(num_per_cat, f)


# In[76]:


# function to get all remaining businesses for each categories
def all_results(url_params, api_key, num_per_cat):
    '''
    url_params: adjust based upon the category and offset value 
    num_per_cat: use num to know how many in each category 
    return a list of remaining businesses after initial 50 restaurants
    for each category 
    '''
    # collect remaining businesses
    businesses = []
    for key, value in num_per_cat.items():
        # only perform api call if the category has more than 50 restaurants
        if value > 50:
            cur = 50  # initial offset is 50
            url_params['categories'] = key  # provide category for url params
            # can only do 1000 offset at a time
            # shouldn't be an issue in this case but just in case
            while cur < value and cur < 1000:
                url_params['offset'] = cur
                # print(key, cur)  # progress tracker
                result = yelp_call(url_params, api_key)
                # just in case if it produces an key error
                businesses.extend(result.json().get('businesses', []))
                # Wait a second
                time.sleep(1)
                # increase offset by 50
                cur += 50
    return businesses


# In[77]:


# url_params for businesses for DC location for all categories of restaurants
location = 'DC'
url_params = {'location': location.replace(' ', '+'),
              'limit': 50
              }
# call all remaining businesses after inital 50 restaurants for each category
businesses_2 = all_results(url_params, api_key, num_per_cat)


# In[214]:


# combine both businesses
total = Businesses+businesses_2
len(total)  # 11536 restaurants


# In[92]:


# if a restaurant in multiple categories
# you may have repeats
# remove duplicates using dictionary
businesses_dict = {}
for rest in total:
    # use restaurant id as unique identifier
    if rest['id'] not in businesses_dict:
        businesses_dict[rest['id']] = rest
# remove almost half , many restaurants share categories
len(businesses_dict)


# In[147]:


# save dictionary for future reference so no need for extra api calls
with open('unique_dict_businessearch.pkl', 'wb') as f:
    pickle.dump(businesses_dict, f)


# In[117]:


# convert the dictionary to a dataframe and remove the index
df_business_search = pd.DataFrame.from_dict(businesses_dict, orient='index')
df_business_search.reset_index(drop=True, inplace=True)
# save the dataframe as pickle for future reference
df_business_search.to_pickle('df_business_search.pkl')


# In[129]:


# create unique restaurant ids for business detail api calls
restaurantids = df_business_search.id


# In[154]:


# create function to get all businesses details using business ids from business search api
def all_results_rest(api_key, restaurantids):
    '''
    restaurantids: unique restaurant ids from business search api, a list of strings 
    return: a list of restaurant details as a list of dictionary 
    '''
    headers = {
        'Authorization': 'Bearer {}'.format(api_key)
    }
    # initialize an empty list
    businesses = []
    # keep track index and restaurantid as it will take over 5000 api calls
    # to get all 6755 restaurants in DC
    for i, id in enumerate(restaurantids):
        # update url with different business ids
        url = 'https://api.yelp.com/v3/businesses/'+id
        # use try and except to prevent too many api call error
        try:
            response = requests.get(url, headers=headers)
            # make sure we get status code 200
            status = response.status_code
            if status != requests.codes.okay:
                # debug print statement
                print(status, i, id)
                break
            else:
                # append business dictionary to the list
                businesses.append(response.json())
        # Wait a second
        time.sleep(1)
        except:
            print(i, id)
            break
    return businesses


# In[175]:


# keep updating restaurantid index to collect all restaurant businesses
# due to api 5000 limit per day
business_details += all_results_rest(api_key, restaurantids[5965:])


# In[218]:


# noticed 404 error for following restaurant id at index 5964
businesses_dict[restaurantids[5964]]
# makes sense as it doesn't have any reviews
# review count and rating are both zero
# documentation says it won't contain businesses with zero reviews


# In[176]:


# we get total 6754 restaurant information in DC area
len(business_details)


# In[177]:


# save the list of business_details as a pickle file
# prevent future api calls
with open('business_details.pkl', 'wb') as f:
    pickle.dump(business_details, f)


# In[220]:


# convert the list into a pandas dataframe
business_details_df = pd.DataFrame(business_details)
# save the business detail dataframe as a pickle file
business_details_df.to_pickle('df_business_details.pkl')


# In[230]:


# check to see if business search contains information
# business details doesn't have and vice versa
# in business_details - business_search
set(business_details_df.columns).difference(set(df_business_search.columns))


# In[232]:


# in business_search - business_details
set(df_business_search.columns).difference(set(business_details_df.columns))


# In[233]:


# Distance in meters from the search location. This returns meters regardless of the locale.
# we will use the business_detail dataframe for analysis 

