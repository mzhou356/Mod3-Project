#!/usr/bin/env python
# coding: utf-8

# # Restaurant Industry Consulting Firm
# July 16, 2019<br>
# Mindy & Ngoc, Helper Functions
# 
# -----------------

# ## Import Needed Libraries

# In[1]:


import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set(style="whitegrid")


# ## For Cleaning

# In[2]:


def split_rows(df, col1, col2, sep):
    '''
    input:
    df: dataframe to use
    col1 and col2 (use col2 to split)
    return:
    a df table with col1 as common col and col2 split into multiple rows
    '''
    series = [pd.Series(row[col1], row[col2].split(sep))
              for _, row in df.iterrows()]
    table = pd.concat(series).reset_index()
    return table


# ## For Inferential Statistics

# In[3]:


class InferentialStatisticsHelperFunctions:
    def bootstrap(self, sample, n):
        '''
        input:
        sample: sample to use (1-d array)
        n: desired size of the sampling sample (int)
        return:
        a list of n random numbers drawn from the input sample with replacement
        '''
        return np.random.choice(sample, size=n, replace=True)
    
    
    def sampling(self, sample, n, num):
        '''
        input:
        sample: sample to use (1-d array)
        n: desired size of the sampling sample (int)
        num: desired size of the sampling method
        return:
        a list of num sampling means
        '''
        sample_means = []
        for i in range(num):
            sample_means.append(self.bootstrap(sample, n).mean())
        return sample_means
    
    
    def top_two_cuisines(self, df, metric):
        '''

        '''
        # Total number of reviews for each cuisine:
        sum_review_by_cuisine = df.groupby("cuisine")[metric].sum()
        # Total number of restaurants for each cuisine:
        count_by_cuisine = df.groupby("cuisine")[metric].count()
        # "Standardized" number of reviews for each cuisine:
        std_sum_review_by_cuisine = sum_review_by_cuisine / count_by_cuisine
        print(std_sum_review_by_cuisine.sort_values(ascending=False).head(2).index)
    
    
    def get_cuisine(self, df, cuisine):
        '''
        
        '''
        new_df = df[df.cuisine == cuisine]
        new_df.reset_index(inplace=True, drop=True)
        df_review_count = new_df.review_count
        df_rating = new_df.rating
        return df_review_count, df_rating
    
    
    def get_bars_open_info(self, df):
        '''
        
        '''
        bars = df[df.cuisine == "Bars"]
        bars.reset_index(inplace=True, drop=True)
        pass_midnight = bars[bars.open_pass_midnight == True]
        pass_midnight.reset_index(inplace=True, drop=True)
        not_pass_midnight = bars[bars.open_pass_midnight == False]
        not_pass_midnight.reset_index(inplace=True, drop=True)
        pass_midnight_review_count = pass_midnight.review_count
        pass_midnight_rating = pass_midnight.rating
        not_pass_midnight_review_count = not_pass_midnight.review_count
        not_pass_midnight_rating = not_pass_midnight.rating
        return pass_midnight_review_count, pass_midnight_rating, not_pass_midnight_review_count, not_pass_midnight_rating
    
    
    def plot_distribution(self, array1, array2, labels, title):
        '''
        array1: 1 d array
        array2: 1 d array
        labels: a list of string for label array1 and array2
        return: histogram plot with 2 plots on the same ax
        '''
        sns.distplot(array1, label=labels[0], color="red")
        sns.distplot(array2, label=labels[1], color="blue")
        plt.ylabel("Probability Density", fontdict={"size":10})
        plt.title(f"Probability Density Plot for {labels[0]} and {labels[1]} - {title}",
                  fontdict={"size": 12})
        plt.legend()
        plt.show()

