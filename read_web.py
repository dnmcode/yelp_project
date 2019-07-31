import os
import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup

abspath = os.path.abspath(sys.argv[0])
main_dir = os.path.dirname(abspath)
os.chdir(main_dir)

# Collect and parse first page
#url = 'https://web.archive.org/web/20121007172955/https://www.nga.gov/collection/anZ1.htm'
#class_include = 'BodyText'
#class_exclude = 'AlphaNav'

num_city = 10
item_per_page = 30
tot_page_num = 2

top_1000_cities = pd.read_csv('us_cities_top_1000.csv')
state_abbrv = pd.read_csv('us_state_abbrv.csv')

city_list = []
for c in range(num_city):
  city = top_1000_cities.iloc[c].city
  state_full = top_1000_cities.iloc[c].state
  state = state_abbrv['Abbreviation'][state_abbrv.index[state_abbrv['State'] == state_full].values[0]]
  city_list.append(', '.join([city, state]))

city_list = ['San Francisco, CA']
#city_list = ['New York, NY']

#url = 'https://www.yelp.com/search?find_desc=Restaurants&find_loc=San%20Francisco%2C%20CA&ns=1&start=0'
div_all_entries = "lemon--div__373c0__1mboc mapColumnTransition__373c0__10KHB arrange-unit__373c0__1piwO arrange-unit-fill__373c0__17z0h border-color--default__373c0__2oFDT"
div_exclude = ''
div_each_entry = "lemon--div__373c0__1mboc largerScrollablePhotos__373c0__3FEIJ arrange__373c0__UHqhV border-color--default__373c0__2oFDT"
div_star = "lemon--div__373c0__1mboc attribute__373c0__1hPI_ display--inline-block__373c0__2de_K u-space-r1 border-color--default__373c0__2oFDT"

keys = ['city', 'state', 'name', 'category', 'star']
data = pd.DataFrame(columns = keys)

print('Importing data...')
for city_idx, city_item in enumerate(city_list):
  print('City (' + str(city_idx + 1) + '/' + str(num_city) + '): ' + city_item)
  page_idx = 1

  while page_idx <= tot_page_num:  
    print('Page: ' + str(page_idx) + '/' + str(tot_page_num))
    
    city_state = city_item.split(',')
    city = city_state[0]
    state = city_state[1]
    
    page_item_start_idx = (page_idx - 1) * item_per_page
    url = 'https://www.yelp.com/search?find_desc=Restaurants&find_loc='+\
          '%2C'.join(city.split(' '))+'%2C%20'+state+'&ns=1&start='+str(page_item_start_idx)
    
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    
    # Pull all text from the div
    all_data = soup.find(class_ = div_all_entries)
    entries = all_data.find_all("div", class_ = div_each_entry)

    for i, item in enumerate(entries[1:]): #entries[0] is not a valid result
      entry = item.find_all('a')
      name = entry[0].contents[0]
      category = []
      for j in range(1, len(entry)):
        category.append(entry[j].contents[0])
      star_str = item.find_all("div", class_ = div_star)[0].find("div").get_attribute_list("aria-label")[0]
      star = star_str.split(' ')[0]
    #  print(name)
    #  print(category)
    #  print(star)
      dict_tmp = {'city':city, 'state':state, 'name':name, 'category':category, 'star':star}
      data = data.append(dict_tmp, ignore_index=True)
    
    page_idx += 1

print('Saving data to csv...')
data.to_csv('data.csv', index=False)
print('Done.')
