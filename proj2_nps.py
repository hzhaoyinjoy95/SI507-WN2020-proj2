#################################
##### Name: Zhaoying He     #####
##### Uniqname: hzhaoyin    #####
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key

state_names = ['alaska', 'alabama', 'arkansas', 'american samoa', 'arizona', 
            'california', 'colorado', 'connecticut', 'district of columbia', 
            'delaware', 'florida', 'georgia', 'guam', 'hawaii', 'iowa', 'idaho', 
            'illinois', 'indiana', 'kansas', 'kentucky', 'louisiana', 'massachusetts', 
            'maryland', 'maine', 'michigan', 'minnesota', 'missouri', 'northern mariana islands', 
            'mississippi', 'montana', 'national', 'north carolina', 'north dakota', 
            'nebraska', 'new hampshire', 'new jersey', 'new mexico', 'nevada', 'new york', 
            'ohio', 'oklahoma', 'oregon', 'pennsylvania', 'puerto rico', 'rhode island', 'south carolina', 
            'south dakota', 'tennessee', 'texas', 'utah', 'virginia', 'virgin islands', 'vermont', 'washington', 
            'wisconsin', 'west virginia', 'wyoming']

BASEURL = 'https://www.nps.gov/index.htm'
CACHE_FILE_NAME = 'cache.json'
CACHE_DICT = {}

headers = {
    'User-Agent': 'UMSI 507 Course Project 2 - Python Scraping and Crawling',
    'From': 'hzhaoyin@umich.edu',
    'Course-Info': 'https://si.umich.edu/programs/courses/507'
}

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, name, category, address, zipcode, phone):
        self.name = name
        self.category = category
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self):
        #Isle Royale (National Park): Houghton, MI 49931, phone
        return f"{self.name} ({self.category}): {self.address} {self.zipcode}"

def load_cache(): 
    ''' Load only once to create a cache file."

    Parameters
    ----------
    None 

    Returns
    -------
    file
        a cache file
    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache): 
    ''' Load whenever the cache file needs to be updated."

    Parameters
    ----------
    cache:
        python file

    Returns
    -------
    None
    '''
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache):
    ''' Check cache to determine whether return from cache or make a new request"

    Parameters
    ----------
    url: string
        url to check 

    cache: dict
        existing cache dictionary

    Returns
    -------
    dict
        key is a url name and value is the url
    '''
    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]     # we already have it, so return it
    else:
        print("Fetching")
        response = requests.get(url,headers=headers) # gotta go get it
        cache[url] = response.text # add the TEXT of the web page to the cache
        save_cache(cache)          # write the cache to disk
        return cache[url]          # return the text, which is now in the cache
    
def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    ## part 1 Scrape state URLs and create a dictionary    
    ## Make the soup
    response = make_url_request_using_cache(BASEURL, CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')

    ## Get the searching-ul
    searching_ul = soup.find('ul',class_='dropdown-menu SearchBar-keywordSearch')
    searching_li = searching_ul.find_all('li')

    # Loop through the search_li to create the url dictionary
    state_url = {}
    for url_state in searching_li:
        url_tag = url_state.find('a')
        state_url[url_state.text.strip().lower()]= 'https://www.nps.gov' + url_tag.get('href')
    return state_url

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    # part 2 create instance from a national site link    
    ## Make the soup
    response = make_url_request_using_cache(site_url, CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')
    # print(soup)
    
    ## Assign information into the class
    #Info Format: Isle Royale (National Park): Houghton, MI 49931
    name = soup.find('a', class_='Hero-title').text.strip()
    category = soup.find('span', class_='Hero-designation').text.strip()
    area = soup.find('span', attrs={'itemprop': "addressLocality"}).text.strip()
    region = soup.find('span', attrs={'itemprop': "addressRegion"}).text.strip()
    address = area + ', ' + region
    zipcode = soup.find('span', attrs={'itemprop': "postalCode"}).text.strip()
    phone = soup.find('span', attrs={'itemprop': "telephone"}).text.strip()
    return NationalSite(name,category,address, zipcode,phone)

def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    #part 3.2 crawling to return list of NationalSite instance
    ## Make the soup for the Courses page
    response = make_url_request_using_cache(state_url, CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')
    
    ## For each national site listed
    site_listing_parent = soup.find('ul', id='list_parks')
    site_listings = site_listing_parent.find_all('li', recursive=False)
    list_national_site_instance = []
    for site_listing in site_listings:
        ## extract the national site details URL
        site_listing_tag = site_listing.find('a')
        site_details_path = site_listing_tag['href']
        course_details_url = "https://www.nps.gov/" + site_details_path + "index.htm"
        national_site_instance = get_site_instance(course_details_url)
        list_national_site_instance.append(national_site_instance)
    return list_national_site_instance

def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    #part 4: find nearby places
    base_url = 'http://www.mapquestapi.com/search/v2/radius?'
    places_params = f"origin={site_object.zipcode}&radius=10&maxMatches=10&ambiguities=ignore&outFormat=json&key={secrets.API_KEY}"
    url = base_url + places_params
    response = make_url_request_using_cache(url, CACHE_DICT)
    result = json.loads(response)
    return result
    

if __name__ == "__main__":
    CACHE_DICT = load_cache()
    state_name = input('Enter a state name (e.g. Michigan, michigan) or \"exit\"\n:')
    while state_name != "exit":
        #part 5 step1 
        if state_name.lower() not in state_names:
            print('[Error] Enter peroper state name')
            state_name = input('Enter a state name (e.g. Michigan, michigan) or \"exit\"\n:')
        else:
            state_name = state_name.lower()
            #part 5 step2
            #create a list of national sites based on state    
            all_state_url_dict = build_state_url_dict()
            state_url_to_call = all_state_url_dict[state_name]
            lists_national_state_instance = get_sites_for_state(state_url_to_call)
            print('----------------------------------------')
            print(f"List of national site in {state_name}")
            print('----------------------------------------')
            num_list = 1
            for national_site_instance_info in lists_national_state_instance:
                print(f"[{num_list}] {national_site_instance_info.info()}")
                num_list += 1

            #part5 step3
            num_result = input('Choose number for detail search or \"exit\" or \"back\"\n:')
            while num_result != "exit":
                if num_result == 'back':
                    state_name = input('Enter a state name (e.g. Michigan, michigan) or \"exit\"\n:')
                    break
                try:
                    num_result = int(num_result)
                    if num_result not in range(len(lists_national_state_instance)):
                        print('[Error] Invalid input')
                        print('--------------------------')
                        num_result = input('Choose number for detail search or \"exit\" or \"back\"\n:')
                except:
                    print('[Error] Invalid input')
                    print('--------------------------')
                    num_result = input('Choose number for detail search or \"exit\" or \"back\"\n:')
                if num_result in range(len(lists_national_state_instance)): 
                    #part5 step4 print nearby places according to user's interger input
                    num_result = int(num_result) - 1
                    results_dict = get_nearby_places(lists_national_state_instance[num_result])['searchResults']
                    print('----------------------------------------')
                    print(f"Places near {lists_national_state_instance[num_result].name}")
                    print('----------------------------------------')
                    for result in results_dict:
                        name = result['name']
                        #check if there is a catrgory
                        if len(result['fields']['group_sic_code_name']) == 0:
                            category = 'no category'
                        else:
                            category = result['fields']['group_sic_code_name']

                        #check if there is a street_address
                        if len(result['fields']['address']) == 0:
                            street_address = 'no address'
                        else:
                            street_address = result['fields']['address']
                    
                        #check if there is a city address
                        if len(result['fields']['city']) == 0:
                            city = 'no city'
                        else:
                            city = result['fields']['city']
                        
                        print(f"- {name} ({category}): {street_address}, {city}")
                    #part5 step5
                    num_result = input('Choose number for detail search or \"exit\" or \"back\"\n:')
    print("Bye!")




