import requests
from bs4 import BeautifulSoup
import time
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

from pathlib import Path

import re 
from datetime import date

# //*[@id="samples-list"]/div/div/div/div[1]/div[2]/div[2]/div/div/button


# make_json()



def get_driver():
	options = webdriver.ChromeOptions()
	##options.add_argument('headless')
	driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
	driver.implicitly_wait(3)

	return driver

# driver = get_driver()

### Make JSON file with collected data ###
def json_output(profile):
	file_exists = os.path.isfile('voice123.json')
	if not file_exists:
		data = {"profiles": []}
		with open("voice123.json", "w+") as file:
			json.dump(data, file, indent=4)
		

	with open("voice123.json", "r+") as file:
		data = json.load(file)
		data['profiles'].append(profile)

		json.dumps(data, indent=4)

	with open("voice123.json", "w+") as file:
		json.dump(data, file, indent=4)
		



### single sample driver ###
def audio_sample(driver):	
	time.sleep(1)	
	sample_soup = BeautifulSoup(driver.page_source, 'lxml')
	sample_name = sample_soup.find('div', {'class': 'sample-name'}).text

	fields    	= sample_soup.find_all('ul', {'class': 'fields'})
	try:
		field_list  = fields[2].find_all('li', {'class': 'field-item'})
	except:
		field_list  = fields[1].find_all('li', {'class': 'field-item'})
	
	sample_languages	= []
	# if len(field_list) < 3:
	# 	sample = {}
	# 	return sample
	try:
		lan 		= field_list[0].find_all('div', {'class': 'interlink'})
		for l in lan:
			l = l.text
			l = l.replace("\n", '')
			l = l.strip()
			sample_languages.append(l)
	except:
		pass
	sample_gender_and_ages	= []
	try:
		
		lan 		= field_list[1].find_all('div', {'class': 'interlink'})
		for g in lan:
			g = g.text
			g = g.replace("\n", '')
			g = g.strip()
			sample_gender_and_ages.append(g)
	except:
		pass

	sample_purposes_of_recording	= []
	try:		
		lan 		= field_list[2].find_all('div', {'class': 'interlink'})
		# name 		= field_list[2].find('span', {'class':'field-name'})
		# print(name.text)
		for p in lan:
			p = p.text
			p = p.replace("\n", '')
			p = p.strip()
			sample_purposes_of_recording.append(p)
	except:
		pass

	#print(field_list)
	download_link = driver.current_url

	sample 	= {
		'sample_name'					: sample_name,
		'sample_languages'				: sample_languages,
		'sample_gender_and_ages'		: sample_gender_and_ages,
		'sample_purposes_of_recording'	: sample_purposes_of_recording,
		'download_link' 				: download_link
	}
	return sample


### single profile page driver & get data ###
def profile_page(profile, driver):
	driver.get(profile)
	print("we are in profile page now...")

	time.sleep(1.5)

	samples = []
	sample_list = driver.find_elements_by_id('samples-list')
	if len(sample_list) == 0:
		try:
			sample_list_div = driver.find_element_by_class_name('playlist')
			sample_list 	= sample_list_div.find_elements_by_class_name('md-list-item')
		except:
			sample_list = []


	s = 0 ### loop through all sample audio ###
	for sample in sample_list:
		try:
			button = sample.find_element_by_class_name('player-title')
			#button.click()	
			driver.execute_script("arguments[0].click();", button)
		except:
			button_div 		= sample.find_element_by_class_name('md-menu')
			button 			= button_div.find_element_by_tag_name('button')
			driver.execute_script("arguments[0].click();", button)

			view_button_div = driver.find_element_by_class_name('md-direction-top-left')
			view_button 	= view_button_div.find_elements_by_tag_name('button')[0]
			driver.execute_script("arguments[0].click();", view_button)
	
		sample_ = audio_sample(driver)
		samples.append(sample_)
		close_section 	= driver.find_element_by_class_name('md-transition-off')
		close_div		= close_section.find_element_by_class_name('modal-title')
		close     		= close_div.find_elements_by_tag_name('button')
		#close[1].click()
		driver.execute_script("arguments[0].click();", close[1])
		s = s+1
		time.sleep(0.5)
		print("Sample No: {}".format(s)) 

	try:
		driver.find_element_by_xpath('//*[@id="about_section"]/div[3]/div/div[2]/button').click()
	except:
		try:
			driver.find_element_by_xpath('//*[@id="about_section"]/div[2]/div/div[2]/div[2]/button').click()
		except:
			pass
	try:
		driver.find_element_by_xpath('//*[@id="services_section"]/div[2]/div/ul/li[6]/ul/li/div/div/div/div/div[2]/button').click()
	except:
		pass
	try:
		driver.find_element_by_xpath('//*[@id="services_section"]/div[2]/div/ul/li[7]/ul/li/div/div/div/div/div[2]/button').click()
	except:
		pass

	time.sleep(1.5)
	soup = BeautifulSoup(driver.page_source, 'lxml')
	#print(soup)
	error = soup.find('div', {'class': 'tdl-error'})
	if error:
		return driver
	try:
		actor_name 			= soup.find('h1', {'class': 'md-headline'}).text
	except:
		actor_name 			= soup.find('span', {'class': 'md-subheading'}).text
	try:
		title 				= soup.find('h2', {'class': 'md-title'}).text
	except:
		title_div 			= soup.find('div', {'class': 'name'})
		title 				= title_div.find('p')
		title 				= title.text



	description 		= soup.find('div', {'class': 'content'})
	if description:
		description = description.text
	else:
		description = ""

	top_percantage 		= ""
	mamber_since 		= ""
	last_active 		= ""
	favorit_point 		= ""

	ranking_container	= soup.find('div', {'class': 'ranking-stat'})
	last_active = ""
	if ranking_container:
		ranking_list 		= ranking_container.find_all('li', {'class': 'md-list-item'})

		favorit_point		= ranking_list[0].find('span',{'class': 'md-title'}).text
		top_percantage   	= ranking_list[1].find('span',{'class': 'md-title'}).text
		mamber_since   		= ranking_list[2].find('span', {'class': 'attribute-value'}).text
		last_active        	= ranking_list[3].find('span', {'class': 'attribute-value'}).text


	else:
		stats_container 	= soup.find('div', {'class':'stats-container'})
		container 			= stats_container.find_all('div', {'class': 'md-list-text-container'})
		i = 0
		try:
			top_percantage = container[i].text
			if 'Top' in top_percantage:
				top_percantage = container[i].find('span', {'class':'md-title'}).text
				i = i+1
			else:
				top_percantage = ""
		except:
			pass

		try:
			respnse_time = container[i].text
			if 'response time' in respnse_time:
				respnse_time = container[i].find('span', {'class':'md-title'}).text
				i = i+1
			else:
				respnse_time = ""

		except:
			pass

		try:
			average_rating = container[i].text
			if 'reviews' in average_rating:
				average_rating = container[i].find('p', {'class':'md-title'}).text
				i = i+1
			else:
				average_rating = ""
		except:
			pass

		try:
			favorit_point = container[i].text
			if 'favorited' in favorit_point:
				favorit_point = container[i].find('span', {'class':'md-title'}).text
				i = i+1
			else:
				favorit_point = ""
		except:
			pass


		main_container 		= soup.find('div', {'class': 'main-content'})
		mamber_since_div 	= main_container.find('div', {'class': 'left'})
		mamber_since 		= mamber_since_div.find('span', {'class': 'attribute-value'}).text





	data_viewer    		= soup.find('div', {'class': 'data-viewer'})
	field_div 			= data_viewer.find_all('div', {'class':'md-list-text-container'})
	
	i = 0
	languages 		= []
	try:
		field_name 		= field_div[i].find('span', {'class': 'field-name'}).text
		if field_name == 'Language':
			interlinks 		= field_div[i].find_all('div', {'class': 'interlink'})
			for l in interlinks:
				l = l.text
				l = l.strip()
				languages.append(l)
			i = i + 1
	except:
		pass

	gender_and_ages	= []
	try:
		field_name 		= field_div[i].find('span', {'class': 'field-name'}).text
		if field_name == "Gender and age":
			interlinks 		= field_div[i].find_all('div', {'class': 'interlink'})
			for g in interlinks:
				g = g.text
				g = g.strip()
				gender_and_ages.append(g)
			i = i+1
	except:
		pass

	additional_services_offered	= []
	try:
		field_name 		= field_div[i].find('span', {'class': 'field-name'}).text
		if field_name == "Additional services offered":
			interlinks 		= field_div[i].find_all('div', {'class': 'md-chip-container'})
			for s in interlinks:
				s = s.text
				s = s.strip()
				additional_services_offered.append(s)
			i = i + 1
	except:
		pass

	jobs_for_these_unions_signatories = []

	try:
		field_name 		= field_div[i].find('span', {'class': 'field-name'}).text
		if field_name == "Jobs for these unions signatories":
			interlinks = field_div[i].find_all('div', {'class': 'interlink'})
			for j in interlinks:
				j = j.text
				j = j.strip()
				jobs_for_these_unions_signatories.append(j)
			i = i+1
	except:
		pass


	recording_and_delivery_options	= []
	try:
		field_name 		= field_div[i].find('span', {'class': 'field-name'}).text
		if field_name == "Recording and delivery options":
			interlinks = field_div[i].find_all('div', {'class': 'md-chip-container'})
			for r in interlinks:
				r = r.text
				r = r.strip()
				recording_and_delivery_options.append(r)
			i = i +1

	except:
		pass

	location	= []
	try:
		field_name 		= field_div[i].find('span', {'class': 'field-name'}).text
		if field_name == "Location":
			interlinks 	= field_div[i].find_all('div', {'class': 'field-value-text'})
			for lo in interlinks:
				lo = lo.text
				lo = lo.strip()
				location.append(lo)
			i = i +1
	except:
		pass

	additional_vocal_abilities = ""
	try:
		field_name 		= field_div[i].find('span', {'class': 'field-name'}).text

		if field_name == "Additional vocal abilities":
	
			additional_vocal_abilities = field_div[i].find('div', {'class': 'content'}).text
			i = i + 1
	except:
		pass

	experience_training_and_equipment = ""
	try:
		field_name 		= field_div[i].find('span', {'class': 'field-name'}).text

		if field_name == "Experience, training, and equipment":
			experience_training_and_equipment = field_div[i].find('div', {'class': 'content'}).text
			i = i + 1
	except: 
		pass

	payment_methods = []
	methods = soup.find_all('li', {'class': 'payment-methods'})
	for method in methods:
		text = method.find('span', {'class': 'attribute-value'}).text
		payment_methods.append(text)

	
	review_section 	= soup.find('div', {'id': 'reviews_section'})
	reviews = 'No review'
	if review_section != None:
		try:
			review_title  	= review_section.find('div', {'class': 'md-title'})
			reviews 		= review_title.find('span').text
		except:
			reviews 		= review_section.find('h2', {'class': 'md-headline'}).text


	profile = {
			'actor_name'	: actor_name,
			'title'			: title,
			'description'	: description,
			'favorit_point'	: favorit_point,
			'top_percantage': top_percantage,
			'mamber_since' 	: mamber_since,
			'last_active'	: last_active,
			'respnse_time' 	: respnse_time,
			'average_rating': average_rating,
			'reviews' 		: reviews,
			'languages'		: languages,
			'gender_and_ages'					: gender_and_ages,
			'additional_services_offered'		: additional_services_offered,
			'jobs_for_these_unions_signatories'	: jobs_for_these_unions_signatories,
			'recording_and_delivery_options'	: recording_and_delivery_options,
			'location'							: location,
			'additional_vocal_abilities'		: additional_vocal_abilities,
			'experience_training_and_equipment'	: experience_training_and_equipment,
			'samples': samples
			}
	json_output(profile)
	return driver 

# driver = get_driver()
# profile = "https://voice123.com/tobyricketts/?sample=13503565"
# x = profile_page(profile ,driver)



### Login function ###
def login(driver):
	print("Going for logging....")
	login_url = "https://accounts.voice123.com/login/?next=%2Fopenid%2Fauthorize%3Fredirect_uri%3Dhttps%253A%252F%252Fvoice123.com%26response_type%3Dcode%26scope%3Dopenid%2520email%26state%3D1a7b681ff4d242f18791a0ac039937da%26nonce%3D1a7b681ff4d242f18791a0ac039937da%26context%3Dwelcome%26client_id%3D450535"
	driver.get(login_url)
	time.sleep(1.5)
	email 		= driver.find_element_by_id('id_login').send_keys('tarek867656@gmail.com')
	password 	= driver.find_element_by_id('id_password').send_keys('tarek@.com')
	button 		= driver.find_element_by_xpath('/html/body/div/div/main/div/div/div/form/div[3]/button').click()
	#driver.execute_script("arguments[0].click();", button)
	time.sleep(2)
	print("Loged in successfully.")
	return driver




### Loop through all pages & get all Profile links from the page ###
def voice_actor_list():
	driver = get_driver()
	driver = login(driver)
	for i in range(1, 1000):
		print("We are in now {} no page..".format(i))
		try:
			list_url = "https://voice123.com/search?service=voice_over&page={}".format(i)
			driver.get(list_url)
		except:
			continue
		time.sleep(4)
		try:
			close = driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/button')
			close.click()
			time.sleep(3)
		except:
			pass
	
		soup = BeautifulSoup(driver.page_source, 'lxml')

		provider_list = soup.find('div', {'class': 'providers'})
		profile_link = provider_list.find_all('a', {'class': 'profile-anchor'})

		for profile in profile_link:
			print(profile.get('href'))
			profile = profile.get('href')
			driver = profile_page(profile, driver)


voice_actor_list()



