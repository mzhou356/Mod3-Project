#!/usr/bin/env python
# coding: utf-8

# # Restaurant Industry Consulting Firm
# July 16, 2019<br>
# Mindy & Ngoc, Helper Functions
# 
# -----------------

# ## Import Needed Libraries

# In[1]:


import warnings
import seaborn as sns
import numpy as np
import pandas as pd
import scipy.stats as stats
import pingouin    # welch F test
from statsmodels.stats.multicomp import pairwise_tukeyhsd, MultiComparison
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
sns.set(style='whitegrid')
warnings.filterwarnings("ignore")


# ## For DataFrame Processing

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


# In[3]:


def splitgroups(df, colname, names):
    '''
    df: dataframe to split the groups 
    colname: name of the column, a string
    names: criteria a list of string to split column of interest
    return: separate dfs, num is length of names, used for split into DC, MD, VA
    '''
    dfs = []
    for i in range(len(names)):
        mask = df[colname] == names[i]
        dfs.append(df[mask].reset_index())
    return dfs


# In[4]:


# split data into high price and low price
def samples(df, colname, criteria, value):
    '''
    df: a dataframe
    colname: colname of interest for split 
    criteria: an int for filter for colname
    value: colname for actual comparsion 
    return 2 samples of 1 day numpy array, data1 uses mask, data2 complement mask
    '''
    mask = df[colname] >= criteria
    data1 = df[mask].reset_index()[value]
    data2 = df[~mask].reset_index()[value]
    return (data1, data2)


# In[5]:


def table_transform(datas, group_names, colname):
    '''
    datas: a list of data for comparision 
    group_names: a list of strings with group names, datas order should be same as group_names
    colname: string, the category to compare 
    return tukeyhsd table result and stacked table 
    create stacked dataframe for tukey_hsd and welch F test
    '''
    df = pd.DataFrame()
    for i in range(len(group_names)):
        df[group_names[i]] = datas[i]
    stacked_df = df.stack().reset_index()
    stacked_df = stacked_df.rename(
        columns={'level_0': 'id', 'level_1': 'state', 0: colname})
    return stacked_df


# ## For Inferential Statistics

# In[9]:


class InferentialStatisticsHelperFunctions():
    '''
    a class for perform inferential statistics 
    '''

    def normality_tests(self, groups_data, group_name, metric_list):
        '''
        groups_data: a list of dataframes for comparision
        group_name: name for the dataframe in groups_data
        metric_list: a list of metrics, such as rating 
        return: df of normal or not normal 
        '''
        df_dict = {}
        for i in range(len(group_name)):
            df_dict[group_name[i]] = {}
            for metric in metric_list:
                # 0.05 is alpha level
                if stats.normaltest(groups_data[i][metric])[1] > 0.05:
                    df_dict[group_name[i]][metric] = 'normal'
                else:
                    df_dict[group_name[i]][metric] = 'not normal'
        return pd.DataFrame(df_dict)

    def variance_tests(self, groups_data):
        '''
        groups_data: a list data of 1 day 
        return: test equal variance or not using stats.levene test 
        '''
        # alpha is 0.05
        if stats.levene(*groups_data)[1] > 0.05:
            return 'equal variance holds'
        else:
            return 'not equal variance '

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

    def sample_category(self, samples, n, num, feature):
        '''
        input:
        samples: a dataframe 
        feature: column name for the dataframe to sample from 
        n: desired size of the sampling sample (int)
        num: desired size of the sampling method
        return:
        a list of num of samples[feature] means 
        '''
        return self.sampling(samples[feature], n, num)

    def one_way_anova(self, groups_data):
        '''
        groups_data: a list data of 1 day 
        return: perform stats.f_oneway to check if there are differences present 
        '''
        # alpha is 0.05
        if stats.f_oneway(*groups_data)[1] > 0.05:
            return 'fail to reject Null Hypothesis'
        else:
            return 'reject Null Hypothesis'

    def tukey_hsd(self, stacked_df, colname):
        '''
        stacked_df: from table_transform, a stacked df 
        colname: string, the category to compare 
        return tukeyhsd table result and stacked table 
        set up tukey hsd for post anova with significance
        '''
        MultiComp = MultiComparison(stacked_df[colname],
                                    stacked_df['state'])
        return MultiComp.tukeyhsd().summary()

    def welch_f_test(self, stacked_df, dependentvar, groupname):
        '''
        stacked_data: a dataframe from table_transform_function
        dependentvar: value to compare 
        groupname: names of group to split 
        return: perform welch F test to check if there are differences present 
        '''
        # alpha is 0.05
        p_value = pingouin.welch_anova(
            dependentvar, groupname, stacked_df)['p-unc'][0]
        if p_value > 0.05:
            return 'fail to reject Null Hypothesis'
        else:
            return 'reject Null Hypothesis'

    def chisquare_test(self, df, category1, category2):
        '''
        df: dataframe with data to compare , pd dataframe
        category1: categorical variable one, string 
        category2: categorical variable two , string 
        return chi square independence result 
        '''
        # create counts for chisquare test
        counts = df.groupby([category1, category2]).size().reset_index()
        # make into proper format for chisquare test
        chi_table = counts.pivot(index=category1, columns=category2, values=0)
        # turn into numpy array
        chi_array = np.array(chi_table)
        if stats.chi2_contingency(chi_array)[1] > 0.05:
            return 'fail to reject Null Hypothesis'
        else:
            return 'reject Null Hypothesis'

    def welch_ttest(self, groups_data, group_name):
        '''
        groups_data: a list data of 1 day 
        group_name: string for groups_data, a list of string
        return: perform stats.ttest_ind, welch to check if there are differences in mean 
        '''
        # alpha is 0.05
        result = stats.ttest_ind(*groups_data, equal_var=False)
        if result[1] > 0.05:
            return 'fail to reject Null Hypothesis'
        elif result[0] > 0:
            return f'{group_name[0]} appears to statistically perform better than {group_name[1]}'
        else:
            return f'{group_name[0]} appears to statistiscally perform worse than {group_name[1]}'

    def price_welcht(self, DF, colname, criteria, metric, n, num, group_name):
        '''
        DF: pd dataframe
        colname: colname to split data, a string
        criteria: a number, criteria for split
        metric: a string, review count or rating 
        n: num of samples for sample mean
        num: num of iteration for sample means
        group_name: string for groups_data, a list of string
        return: welcht test result 
        '''
        price_splits = samples(DF, colname, 2, metric)
        price_high = price_splits[0]
        price_low = price_splits[1]
        # sampling
        high_means = np.array(self.sampling(price_high, n, num))
        low_means = np.array(self.sampling(price_low, n, num))
        return self.welch_ttest([high_means, low_means], group_name)

    def top_two_cuisines(self, df, metric):
        '''

        '''
        # Total number of reviews for each cuisine:
        sum_review_by_cuisine = df.groupby("cuisine")[metric].sum()
        # Total number of restaurants for each cuisine:
        count_by_cuisine = df.groupby("cuisine")[metric].count()
        # "Standardized" number of reviews for each cuisine:
        std_sum_review_by_cuisine = sum_review_by_cuisine / count_by_cuisine
        print(std_sum_review_by_cuisine.sort_values(
            ascending=False).head(2).index)

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

    def plot_distribution(self, array1, array2, labels, featurename):
        '''
        array1: 1 d array
        array2: 1 d array
        labels: a list of string for label array1 and array2
        return: histogram plot with 2 plots on the same ax
        '''
        sns.distplot(array1, label=labels[0], color='red')
        sns.distplot(array2, label=labels[1], color='blue')
        plt.ylabel('probability density', fontdict={'size': 10})
        plt.title(f'{featurename} Probability Density Plot for'
                  f'{labels[0]} and {labels[1]}', fontdict={
                      'size': 12})
        plt.legend()
        plt.show()


# ## For Plotting 

# In[7]:


def plothist(join_df, df):
    '''
    join_df: dataframe containing all DC, MD, VA
    df: a list of separate dataframes, DC, MD, VA
    return a 2 by 2 histogram plot for comparision 
    '''
    fig = plt.figure(figsize=(8, 6))
    fig.add_subplot(221)
    plt.hist(join_df.price, label='Metroplex',
             color='red', bins=4, density=True)
    plt.legend()
    fig.add_subplot(222)
    plt.hist(df[0].price, label='DC', color='blue', bins=4, density=True)
    plt.legend()
    fig.add_subplot(223)
    plt.hist(df[1].price, label='MD', color='green', bins=4, density=True)
    plt.legend()
    fig.add_subplot(224)
    plt.hist(df[2].price, label='VA', color='purple', bins=4, density=True)
    plt.legend()
    plt.show()

