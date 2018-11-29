from bs4 import BeautifulSoup
import requests
import re
import json


def one_page_parser(url):
    try:
        r = requests.get(url)
    except Exception as e:
        print("We can't connect to server www.park.by.")
        exit()

    r.encoding = 'windows-1251'  # set the right encoding of webpage (the identical encoding is 'cp1251' or 'ansi')
    # r.encoding = 'windows-1252' # uncomment this line, and comment a line above to parse webpage in English language (the identical encoding is 'cp1252')
    source = r.text  # get html webpage

    soup = BeautifulSoup(source, 'html5lib')  # with this parser library there is no problems with &QUOT; and etc., and aka broken html

    companies_data_list_one_page = list()  # list to store all companies data

    # for all div elements (inforamation for one company) on webpage
    for div_element in soup.find_all('div', 'it_enterprise_intro'):

        company_data_dict = dict()  # dictionary to store each company data

        name = div_element.h2.text  # get company name

        links_list = div_element.find_all('a', class_='morelink')  # find all links within div container
        detailed_description_ref = links_list[0]['href']  # get relative link to detailed company description
        detailed_description_link = f'http://www.park.by{detailed_description_ref}'

        # check, if there are two links (one is for detailed description, second is for projects) and get relative link to company's projects, if there is any
        if len(links_list) == 2:
            projects_ref = links_list[1]['href']
            projects_link = f'http://www.park.by{projects_ref}'
        else:
            projects_link = None

        start_pattern = re.compile(r'\B</h2>')  # \B - Not a Word Boundary
        stop_pattern = re.compile(r'\B<a')

        str_div_element = div_element.prettify()  # nicely formatted string
        start = re.search(start_pattern, str_div_element).end()  # find where </h2> tag ends
        end = re.search(stop_pattern, str_div_element).start()  # find where <a> tag starts

        text_with_tags = str_div_element[start:end]  # slice only company's description section from </h2> tag till <a> tag

        text = re.sub(r'<[^>]+>', '', text_with_tags)  # get rid of tags withtin section

        description = re.sub(r'[\s]+', ' ', text)  # get rid of unnessasary spaces
        description = description.strip()

        # store data for each company in Python dictionary
        company_data_dict['name'] = name
        company_data_dict['description'] = description
        company_data_dict['detailed description link'] = detailed_description_link
        company_data_dict['projects link'] = projects_link

        companies_data_list_one_page.append(company_data_dict)

    return companies_data_list_one_page


# url = 'http://www.park.by/it/enterprises/'  # first page

companies_data_list = []  # list of data for all pages

for i in range(0, 35): # crawl pages from 1 to 35
    url = f'http://www.park.by/it/enterprises/?start={i}'
    one_page_data = one_page_parser(url)
    companies_data_list.extend(one_page_data)

all_data = dict()
all_data['companies'] = companies_data_list

# write received data to file using JSON format
with open('park_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(all_data, json_file, ensure_ascii=False, indent=2)
