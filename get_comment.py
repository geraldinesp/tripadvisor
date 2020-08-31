# Author: Francois LASSERRE <github@choiz.fr>
# Author: Geraldine SULCA POLO <geraldine.sul@gmail.com>
# Copyright 2020 - All rights reserved
#
# Master 2 IREN - Dissertation 2020

# import packages that we need
import sys
import csv
from urllib.request import urlopen
import urllib.request
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException

debug=False
skipnext=False
nb_com=0
nb_rep=0
colonnes = 5
ratings = {"1":0,"2":0,"3":0,"4":0,"5":0}
ratings_answer = {"1":0,"2":0,"3":0,"4":0,"5":0}

# check if filename exist in cache
def cache_exists(filename):
    try:
        # write current page in cache
        with open('cache/'+filename, 'r') as cache_file:
            if debug:
                print('cache for this page exists')
            return cache_file.read()
    except:
        if debug:
            print('cache for this page doesn\'t exist yet!')
        return False

# split url in multiple parts
def get_url_path(url):
    if debug:
        print('call: get_url_path() '+url)
    parse = urlparse(url)
    if debug:
        print('url.path: '+parse.path)
    return parse.path

# get protocol and domain name from an url
def get_url_location(url):
    if debug:
        print('call: get_url_path() '+url)
    parse = urlparse(url)
    if debug:
        print('url.scheme: '+parse.scheme)
        print('url.netloc: '+parse.netloc)
    return parse.scheme+'://'+parse.netloc

# download page content and create cache if not exists
def get_page(url):
    if debug:
        print('call: get_page() '+url)
# get the filename from the complete url
    filename = get_url_path(url)
    if debug:
        print('filename: '+filename)
    cache_page_content = cache_exists(filename)
    if cache_page_content:
        if debug:
            print('le cache existe')
        return cache_page_content
    else:
        if debug:
            print('le cache n\'existe pas')
        # cache doesn't exits
        # download the page content
        page = urllib.request.urlopen(url)
        page_content = page.read()
        if url != page.geturl():
            return False
        # create empty cache file
        cache_file=open('cache/'+filename, 'wb')
        # write page content in cache
        cache_file.write(page_content)
        cache_file.close()
        return page_content

# count ratings (ex: note_client = 3)
def nb_rating(note_client):
    # ratings[3] = ratings[3] + 1
    ratings[note_client] = ratings[note_client]+1


# count ratings answers
def nb_rating_answer(note_client):
    ratings_answer[note_client] = ratings_answer[note_client]+1

# define comments and answers function
def get_comments_and_answers(soup, restaurant_id, page):
    print("PAGE : "+str(page))
    print("")
    print("Commentaires : ")
    print("===============")
    comment_id = 0
    index=0
    index2=0
    ##add list object element2

    global nb_com
    global nb_rep
    global skipnext
    while comment_id < len(soup.find_all(class_="reviewSelector")):
        if skipnext:
            comment_id = comment_id+1
            skipnext = Falsenote

            continue;
        # get number of page of reviews
        #number_of_page=soup.find(class_="pageNum last cx_brand_refresh_phase2").text
        # print("Nombre de page :"+number_of_page)
        # get the node member in html
        member = soup.find_all(class_="reviewSelector")[comment_id].find(class_="info_text").find('div').get_text()
        print("Auteur : "+member)
        # get the node badge "number of reviews of each member" in html
        #badge = soup.find_all(class_="reviewSelector")[comment_id].find(class_="badgeText").get_text().replace('avis', '')
        #print("Avis : "+badge)
        # get the node date in html
        date = soup.find_all(class_="reviewSelector")[comment_id].find(class_="ratingDate").get_text()
        print(date)
        # get the node note_client (individual note) in html
        note_client = get_note(soup.find_all(class_="reviewSelector")[comment_id].find(class_="ui_bubble_rating").get("class")[1])
        print("Note client : "+note_client)
        # get the node title (verbatim) in html
        title = soup.find_all(class_="reviewSelector")[comment_id].find(class_="noQuotes").get_text()
        print("Titre : "+title)
        # get the node commentaire in html
        commentaire = soup.find_all(class_="reviewSelector")[comment_id].find(class_="prw_reviews_text_summary_hsx").find('div').find('p')
        # get all the rewiew with browser and save the result on web element2
        element2=browser.find_elements_by_class_name("partial_entry")
        # get the specific rewiew
        if index < len(element2):
            com = element2[index].text
            nb_com=nb_com+1
        # display the review
        print("Commentaire: " +com)
        print("")
        # get the node reponse in html
        response=commentaire.parent.parent.parent.find(class_="mgrRspnInline")
        # get all the response with browser and save the result on web element3
        element3 = browser.find_elements_by_class_name("mgrRspnInline")

        # if comment had an answer from the restaurant
        if response is not None:

            if index2 < len(element3):
                res = element3[index2].text
                print("=== Reponse du restaurant : ===")
                res1 = res.split("\n")
                # remove 2 first lines
                res1.pop(0)
                res1.pop(0)
                # remove 2 last lines if (2nd from the end is afficher moins)
                if len(res1) > 2:
                    if res1[-2] == 'Afficher moins':
                        res1.pop(-1)
                        res1.pop(-1)
                reponse_resto = "\n".join(res1)
                print(reponse_resto)
                nb_rep=nb_rep+1
                index=index+1
                index2=index2+1
                nb_rating_answer(note_client)

        # if comment had no answer from the restaurant
        else:
            reponse_resto = ""
            print("Pas de reponse a ce commentaire")
        print("")
        print("---")
        print("")
        comment_id = comment_id + 1
        index=index+1
        # save the information of restaurant on table & write the result on CSV file

        restaurant_list=[restaurant_id, member, note_client, title, com, reponse_resto]
        with open('reviews_.csv', 'a',encoding="utf-8") as fich:
                writer= csv.writer(fich, delimiter=";")
                writer.writerow(restaurant_list)

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

def get_notes_by_type(arg):
    i = 0
    j = 1
    for notes in arg:
      print(arg[i].find(class_="_2vS3p6SS").get_text()+": "+get_note(soup.find_all(class_="ui_bubble_rating")[j].get("class")[1]))
      i=i+1
      j=j+1

# Starting!
urls_to_scrap = [
'https://www.tripadvisor.fr/Restaurant_Review-g187147-d695211-Reviews-Brasserie_Balzar-Paris_Ile_de_France.html',
'https://www.tripadvisor.fr/Restaurant_Review-g187147-d1141250-Reviews-La_Grille_Montorgueil-Paris_Ile_de_France.html',
'https://www.tripadvisor.fr/Restaurant_Review-g187147-d714974-Reviews-Chez_Lena_et_Mimile-Paris_Ile_de_France.html',
'https://www.tripadvisor.fr/Restaurant_Review-g187147-d2217897-Reviews-Les_Cascades-Paris_Ile_de_France.html',
'https://www.tripadvisor.fr/Restaurant_Review-g187147-d1392640-Reviews-Restaurant_Tout_Le_Monde_En_Parle-Paris_Ile_de_France.html',
'https://www.tripadvisor.fr/Restaurant_Review-g187147-d4553851-Reviews-La_Petite_Place-Paris_Ile_de_France.html',
'https://www.tripadvisor.fr/Restaurant_Review-g187147-d8064902-Reviews-La_Source-Paris_Ile_de_France.html',
'https://www.tripadvisor.fr/Restaurant_Review-g187147-d7245681-Reviews-Maison_Pradier_Saint_Lazare-Paris_Ile_de_France.html',
'https://www.tripadvisor.fr/Restaurant_Review-g187147-d14072860-Reviews-Les_Belles_Plantes-Paris_Ile_de_France.html'
]

for url_to_scrap in urls_to_scrap:
    page_content = get_page(url_to_scrap)
    soup = BeautifulSoup(page_content, "html.parser")
    print("")

    #restaurant_name = soup.find_all(class_="_3a1XQ88S")[0].get_text()
    #print("Restaurant : "+restaurant_name)
    restaurant_id = soup.find_all(class_="BY2BR2sP ui_link")[0]['href'].replace('/UpdateListing-','')
    print("Restaurant_id : "+restaurant_id)
    note = soup.find_all(class_="r2Cf69qf")[0].get_text().replace(',','.')
    print("Note : "+note)
    nb_avis = soup.find_all(class_="_10Iv7dOs")[0].get_text().replace('avis', '')
    nb_avis = re.sub(r"\s+", '', nb_avis)
    print("Nombre d'avis : "+nb_avis)
    excellent = soup.find_all(class_="row_num is-shown-at-tablet")[0].get_text()
    print("Excellent : "+excellent)
    tresbon = soup.find_all(class_="row_num is-shown-at-tablet")[1].get_text()
    print("Tres bon : "+tresbon)
    moyen = soup.find_all(class_="row_num is-shown-at-tablet")[2].get_text()
    print("Moyen : "+moyen)
    mediocre = soup.find_all(class_="row_num is-shown-at-tablet")[3].get_text()
    print("Mediocre : "+mediocre)
    horrible = soup.find_all(class_="row_num is-shown-at-tablet")[4].get_text()
    print("Horrible : "+horrible)
    get_notes_by_type(soup.find_all(class_="jT_QMHn2"))

    restaurant_info=[restaurant_id, note, nb_avis, excellent, tresbon, moyen, mediocre, horrible]
    with open('restaurants_.csv', 'a',encoding="utf-8") as fich:
      writer= csv.writer(fich, delimiter=";")
      writer.writerow(restaurant_info)

    page = 0
    while page <= 9:
        if page == 0:
            # call browser by webdrivet
            browser=webdriver.Chrome('./chromedriver/chromedriver')
            url = url_to_scrap
            # get url to the browser
            browser.get(url)
            # find element with browser that contain css selector PLUS
            browser.find_element_by_css_selector('.taLnk.ulBlueLinks').click()
            element2=browser.find_elements_by_class_name("partial_entry")
            get_comments_and_answers(soup, restaurant_id, page)
            browser.quit()
        else:
            url_splited = url_to_scrap.split('Reviews-', 1)
            # new_url = 'Restaurant_Review-g187147-d19318900-' + 'Reviews-or' + str(page) + '0-' + 'La_Table_de_Colette-Paris_Ile_de_France.html'
            new_url = url_splited[0]+'Reviews-or'+str(page)+'0-'+url_splited[1]
            # get page content
            page_content = get_page(new_url)
            print(new_url)
            # try if Plus exist then call browser to click on it
            try:
                browser=webdriver.Chrome('./chromedriver/chromedriver')
                browser.get(new_url)
                browser.find_element_by_css_selector('.taLnk.ulBlueLinks').click()
                element2=browser.find_elements_by_class_name("partial_entry")
                if page_content != False:
                    soup = BeautifulSoup(page_content, "html.parser")
                    # get comments for this page
                    get_comments_and_answers(soup, restaurant_id, page)
                    browser.quit()
                else:
                    page = 100
                    browser.quit()

            except StaleElementReferenceException:
                element2=browser.find_elements_by_class_name("partial_entry")
                if page_content != False:
                    soup = BeautifulSoup(page_content, "html.parser")
                    # get comments for this page
                    get_comments_and_answers(soup, restaurant_id, page)
                    browser.quit()
                else:
                    page = 100
                    browser.quit()
            except ElementNotInteractableException:
                element2=browser.find_elements_by_class_name("partial_entry")
                if page_content != False:
                    soup = BeautifulSoup(page_content, "html.parser")
                    # get comments for this page
                    get_comments_and_answers(soup, restaurant_id, page)
                    browser.quit()
                else:
                    page = 100
                    browser.quit()
            # call an exception when the CSS selector Plus don't exist
            except NoSuchElementException:
                element2=browser.find_elements_by_class_name("partial_entry")
                if page_content != False:
                    soup = BeautifulSoup(page_content, "html.parser")
                    # get comments for this page
                    get_comments_and_answers(soup, restaurant_id, page)
                    browser.quit()
                else:
                    page = 100
                    browser.quit()

        #incrementation to go to the next page of restaurant
        page = page + 1
