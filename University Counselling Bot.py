# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 13:40:47 2023

@author: Admin
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.wait import WebDriverWait
import os
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support.ui import WebDriverWait


from selenium.common.exceptions import NoSuchElementException



driver = webdriver.Chrome (service = Service (ChromeDriverManager().install()))
Course = input(str('Enter Your Course Name: '))
# bachelor of data science
#driver = webdriver.Chrome (service = Service (ChromeDriverManager().install()))

driver.get ('https://www.uac.edu.au/course-search/undergraduate/find-a-course.html')
time.sleep (5)

#Search for course based on input
searchbox = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[2]/fieldset/div/div/form/input")
searchbox.send_keys(Course + Keys.RETURN)

# Click institution button
button=driver.find_element( By.XPATH, value = '//*[@id="filterSectionInst"]/button')
button.click()

# Filter 5 required universities            
time.sleep (5)
# Macquarie
driver.find_element( By.XPATH,  '//*[@id="filterSectionInst"]/div/div[12]/label/input').click()
time.sleep (1)
# University of Sydney
driver.find_element( By.XPATH,  '//*[@id="filterSectionInst"]/div/div[23]/label/input').click()
time.sleep (1)
# UTS
driver.find_element( By.XPATH,  '//*[@id="filterSectionInst"]/div/div[24]/label/input').click()
time.sleep (1)
# UNSW
driver.find_element( By.XPATH,  '//*[@id="filterSectionInst"]/div/div[26]/label/input').click()
time.sleep (1)
# Western Sydney
driver.find_element( By.XPATH,  '//*[@id="filterSectionInst"]/div/div[27]/label/input').click()
time.sleep (1)

#Show all courses
try:
    
    driver.find_element( By.XPATH,  '//*[@id="course-search-container"]/div[2]/div[2]/div[2]/div[17]/div/span/a').click()
    time.sleep (5)
    # Scroll the webpage to the top of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollTop);")
except NoSuchElementException:
    print ('Course Not Found')
    

course_links = []
uni_infos = []
atars = []
prerequisites = []


# Find all the course links
i = 2
while True:
    try:
        
        element = driver.find_element (By.XPATH, f'//*[@id="course-search-container"]/div[2]/div[2]/div[2]/div[{i}]/div[2]/p/a')
        course_link = element.get_attribute ('href')
        course_links.append (course_link)
        i += 1
    except NoSuchElementException:
        break

print(course_links[0])
print(len(course_links))



#Get all the information from each course
for course in course_links:
    driver.get (course)
    # Find uni name of the course
    uni_name = driver.find_element (By.XPATH, '/html/body/div[3]/div/p[3]').text
    i = 2
    while True:
        try:
            # Find the table with university info
            uni_info = driver.find_element (By.XPATH, f'//*[@id="course-details"]/div[3]/div[{i}]').text
            uni_info = uni_info.split('\n')
            uni_info.insert (0, uni_name)
            uni_infos.append (uni_info)
            
            
            # Find the atar table and get the atar
            atar = driver.find_element (By.XPATH, f'//*[@id="atarDataTable"]/tbody/tr[{i-1}]').text
            atar = atar.split (' ')
            
            atars.append (atar)
            i += 1
            try:
                prereq = driver.find_element (By.XPATH, '//*[@id="prereq"]/p').text.replace ('\n', ' ')
                prerequisites.append (prereq)
            except NoSuchElementException:
                prerequisites.append (None)
                pass
            
        except NoSuchElementException:
            break
print(uni_infos[0])
print(atars[0])
print(prerequisites[0]) 

#import pandas as pd
uni_df = pd.DataFrame(uni_infos)
atar_df = pd.DataFrame(atars)

#print(uni_df.head())
#print(atar_df)

column_names = {
    0: 'University Name',
    1: 'Course',
    2: 'Location',
    3: 'Code',
    4: 'Fee',
    5: 'Duration'
}


# Rename column names of uni_df dataframe
uni_df.rename (columns = column_names, inplace = True)
#print(uni_df.head())

# Add pre-requisites column into the dataframe
uni_df['Prerequisites'] = prerequisites
#print(uni_df.head())

# Join all the start dates into 1 column
startDates = pd.Series(uni_df[uni_df.columns[6:]].apply(
    lambda x: ','.join(x.dropna().astype(str)),
    axis=1
))

uni_df.insert(loc=6, column='Start Dates', value=startDates)

# Drop unnecessary columns
uni_df.drop (uni_df.iloc[:, 7:], axis = 1, inplace = True)

atar_df.columns = ['Code', 'LowestATAR', 'MedianATAR', 'HighestATAR', 'LowestSelectionRank', 'MedianSelectionRank', 'HighestSelectionRank']
#print(atar_df.head())

# Merge uni_df with atar_df
full_df = uni_df.merge (atar_df, on = ['Code'], how = 'left')
print(full_df.head())

# Reset the index
full_df = full_df.reset_index().drop (columns = ['index'])

# Filter and choose only courses with 3F duration
full_df = full_df.loc[full_df['Duration'].str.contains ('3F')==True]

full_df = full_df.drop_duplicates(subset = ['Code'], keep = 'first')

# Export the output
#full_df.to_csv ('uni_infos_output.csv')

import os
cwd = os.getcwd()
print (cwd)
crs_name = Course.replace(' ', '_')
full_df.to_csv(f'{cwd}/{crs_name}_course.csv')

print (f'csv file located at {cwd}/{crs_name}_course.csv')
