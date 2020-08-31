import csv
import time
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import platform

#url_to_scrap = "https://www.tripadvisor.fr/Restaurants-g187147-Paris_Ile_de_France.html"
#url_to_scrap = "https://www.tripadvisor.fr/RestaurantSearch-g187147-oa330-a_date.2020__2D__07__2D__26-a_people.2-a_time.20%3A00%3A00-a_zur.2020__5F__07__5F__26-Paris_Il.html"
url_to_scrap = "https://www.tripadvisor.fr/RestaurantSearch-g187147-oa720-a_date.2020__2D__07__2D__26-a_people.2-a_time.20%3A00%3A00-a_zur.2020__5F__07__5F__26-Paris_Il.html"
#url_to_scrap = "https://www.tripadvisor.fr/RestaurantSearch-g187147-oa10440-a_date.2020__2D__07__2D__26-a_people.2-a_time.20%3A00%3A00-a_zur.2020__5F__07__5F__26-Paris_Il.html"
#url_to_scrap = "https://www.tripadvisor.fr/RestaurantSearch-g187147-oa5010-a_date.2020__2D__07__2D__26-a_people.2-a_time.20%3A00%3A00-a_zur.2020__5F__07__5F__26-Paris_Il.html#EATERY_LIST_CONTENTS"
#url_to_scrap = "https://www.tripadvisor.fr/RestaurantSearch-g187147-oa16710-a_date.2020__2D__07__2D__26-a_people.2-a_time.20%3A00%3A00-a_zur.2020__5F__07__5F__26-Paris_Il.html#EATERY_LIST_CONTENTS"

if platform.system() == "Darwin":
	driver = webdriver.Chrome('./chromedriver')
elif platform.system() == "Win32":
	driver = webdriver.Chrome('C:/Windows/chromedriver.exe')
#elif platform.system() == "Linux" or platform == "Linux2":
#    driver = webdriver.Chrome('./chromedriver')


print("Getting URL...")
driver.get(url_to_scrap)

# function to check if the button is on the page, to avoid miss-click problem
def check_exists_by_xpath(xpath):
	try:
		driver.find_element_by_xpath(xpath)
	except NoSuchElementException:
		return False
	return True


# translate classname into integer note
def get_note(arg):
	if arg == "bubble_50":
		return "5"
	if arg == "bubble_45":
		return "4.5"
	if arg == "bubble_40":
		return "4"
	if arg == "bubble_35":
		return "3.5"
	if arg == "bubble_30":
		return "3"
	if arg == "bubble_25":
		return "2.5"
	if arg == "bubble_20":
		return "2"
	if arg == "bubble_15":
		return "1.5"
	if arg == "bubble_10":
		return "1"
	if arg == "bubble_05":
		return "0.5"
	if arg == "bubble_00":
		return "0"
	else:
		return "NaN"

def get_prix(arg):
	if arg == "€":
		return "Repas economique"
	if arg == "€€-€€€":
		return "Intermediaire"
	if arg == "€€€€":
		return "Cuisine raffinee"
	else:
		return arg

# Get restaurant details from info page
def get_details(soup, url):
	if soup.find_all(class_="_3a1XQ88S"):
		restaurant_name = soup.find_all(class_="_3a1XQ88S")[0].get_text()
	else:
		restaurant_name = None
	print("Restaurant name: "+str(restaurant_name))
	
	#restaurant_id = url[53:60]
	restaurant_id = soup.find_all(class_="BY2BR2sP ui_link")[0]['href'].replace('/UpdateListing-','')
	print('Restaurant ID: '+restaurant_id)
	
	if soup.find_all(class_="_1NXh105y"):
		attribution = soup.find_all(class_="_1NXh105y")[0].get_text()
	else:
		attribution = None
	print("Attribution status:" +str(attribution))
	
	if soup.find_all(class_="r2Cf69qf"):
		rating = soup.find_all(class_="r2Cf69qf")[0].get_text().replace(',','.')
	else:
		rating = None
	print("Rating: "+str(rating))

	restaurant_type = []
	if len(soup.find_all(class_="_2mn01bsa")) != 0:
		print("Number of caracteristics: "+ str(len(soup.find_all(class_="_2mn01bsa"))))
		for i in range(0,len(soup.find_all(class_="_2mn01bsa"))):
			#print(soup.find_all(class_="_2mn01bsa")[i].get_text())
			restaurant_type.append(str(soup.find_all(class_="_2mn01bsa")[i].get_text()))
		for i in range(len(soup.find_all(class_="_2mn01bsa")),5):
			restaurant_type.append('-')
	else:
		for i in range(0,5):
			restaurant_type.append('-')
	#print("Restaurant caracteristics: "+str(restaurant_type))

	price_idx = [i for i, item in enumerate(restaurant_type) if re.search('€$', item)]
	if price_idx:
		restaurant_type.append('-')
		if price_idx[0]>0:
			restaurant_type.insert(0, restaurant_type.pop(price_idx))
	else:
		restaurant_type.insert(0, '-')
	print("Restaurant caracteristics: "+str(restaurant_type))

	if soup.find_all(class_="_2VxaSjVD"):
		ranking_general = soup.find_all(class_="_2VxaSjVD")[0].get_text()
	else:
		ranking_general = None
	print("General ranking: "+ str(ranking_general))

	if soup.find_all(class_="_3-W4EexF"):
		ranking_cuisinetype = soup.find_all(class_="_3-W4EexF")[0].get_text()
	else:
		ranking_cuisinetype = None
	print("Cuisine ranking: "+ str(ranking_cuisinetype))

	
	address = soup.find_all(class_="_2saB_OSe")[0].get_text()
	print("Address: "+address)
	
	if soup.find_all(class_="_10Iv7dOs"):
		nb_avis = soup.find_all(class_="_10Iv7dOs")[0].get_text().replace('avis', '')
		nb_avis = re.sub(r"\s+", '', nb_avis)
	else:
		nb_avis = 0
	print("Number of reviews: "+str(nb_avis))

	# get number of page of reviews
	if soup.find(class_="pageNum last cx_brand_refresh_phase2") != None:
		number_of_page = soup.find(class_="pageNum last cx_brand_refresh_phase2").text
	else:
		number_of_page = 1
		print("Number of pages FR: "+str(number_of_page))
	
	if soup.find_all(class_="_10Iv7dOs"):
		excellent = soup.find_all(class_="row_num is-shown-at-tablet")[0].get_text()
		print("Reviews Excellent FR: "+excellent)
		verygood = soup.find_all(class_="row_num is-shown-at-tablet")[1].get_text()
		print("Reviews Very good FR: "+verygood)
		medium = soup.find_all(class_="row_num is-shown-at-tablet")[2].get_text()
		print("Reviews Medium FR: "+medium)
		mediocre = soup.find_all(class_="row_num is-shown-at-tablet")[3].get_text()
		print("Reviews Mediocre FR: "+mediocre)
		horrible = soup.find_all(class_="row_num is-shown-at-tablet")[4].get_text()
		print("Reviews Horrible FR: "+horrible)
	else:
		excellent = 0
		print("Reviews Excellent FR: 0")
		verygood = 0
		print("Reviews Very good FR: 0")
		medium = 0
		print("Reviews Medium FR: 0")
		mediocre = 0
		print("Reviews Mediocre FR: 0")
		horrible = 0
		print("Reviews Horrible FR: 0")

	if soup.find_all(class_="_377onWB-"):
		cuisine = get_note(soup.find_all(class_="ui_bubble_rating")[1].get("class")[1])
		print("Rating Cuisine: "+cuisine)
		service = get_note(soup.find_all(class_="ui_bubble_rating")[2].get("class")[1])
		print("Rating Service: "+service)
		ratio = get_note(soup.find_all(class_="ui_bubble_rating")[3].get("class")[1])
		print("Rating Price-quality ratio: "+ratio)
		ambiance = get_note(soup.find_all(class_="ui_bubble_rating")[4].get("class")[1])
		print("Rating Ambiance: "+ambiance)
	else:
		cuisine = None
		print("Rating Cuisine: 0")
		service = None
		print("Rating Service: 0")
		ratio = None
		print("Rating Price-quality ratio: 0")
		ambiance = None
		print("Rating Ambiance: 0")

	print("\n")
	#return(restaurant_name, id_restaurant, attribution, note, prix, classement_general, classement_typecuisine, adresse, nb_avis, number_of_page, excellent, tresbon, moyen, mediocre, horrible, cuisine, service, rapport, ambiance, url)
	return(restaurant_name, restaurant_id, attribution, rating, restaurant_type[0], restaurant_type[1], restaurant_type[2], restaurant_type[3], restaurant_type[4], ranking_general, ranking_cuisinetype, address, nb_avis, number_of_page, excellent, verygood, medium, mediocre, horrible, cuisine, service, ratio, ambiance, url) 

# open the file to save the review
csvFile = open("./reviews.csv", 'a')
csvWriter = csv.writer(csvFile)

# CSS classes for needed items
# next button
next_button_xpath= '//a[@class="nav next rndBtn ui_button primary taLnk"]'

# review container
review_div_class = "_2Q7zqOgW"
restaurant_name_div_class= "_15_ydu6b"

i=1
numero_page=1
dict_restaurant=dict()
# change the value inside the range to save more or less reviews
while check_exists_by_xpath(next_button_xpath):
	print('########## Numero page : '+str(numero_page)+' ##########')
	if numero_page<0 :
		try:
			driver.find_element_by_xpath(next_button_xpath).click()
			time.sleep(4)
			numero_page=numero_page+1
		except:
			print("Erreur Next **********")
	else :
		soup = BeautifulSoup(driver.page_source, 'lxml')
		reviews_html = soup.find_all("div", class_=review_div_class)
		with open("./reviews.csv", 'a') as csv_file:
			csv_out = csv.writer(csv_file, delimiter=';')
			for review in reviews_html:
				print("Numero restaurant : "+str(i))
				try:
					soup = BeautifulSoup(driver.page_source, 'lxml')
					name = review.find(class_=restaurant_name_div_class)
					# Avoid sponserd listings, those starting with a number are not sponsored
					if name.get_text()[0].isdigit():
						url_open='https://www.tripadvisor.fr'+name.get('href')
						print(name.get('href'))
						if(url_open in dict_restaurant):
							print("Restaurant existant")
						else :
							dict_restaurant.setdefault(url_open, url_open)
							info_page_html = urlopen(url_open, timeout=40).read()
							soup = BeautifulSoup(info_page_html, 'lxml')
							details = get_details(soup, url_open)
							csv_out.writerow(details)
							i=i+1
				except:
					print("Erreur URL")

		# Click on 'next' button
		try:
			driver.find_element_by_xpath(next_button_xpath).click()
			time.sleep(4)
			numero_page=numero_page+1
		except:
			print("Erreur Next **********")

driver.close()
