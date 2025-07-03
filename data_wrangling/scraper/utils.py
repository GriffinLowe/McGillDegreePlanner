from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup

def get_page(url:str, timeout=100) -> BeautifulSoup:
    '''
    Fetches and parses an HTML page into a BeautifulSoup object.

    This function sends a GET request to the specified URL with a custom 
    User-Agent header to mimic a browser. If successful, it returns a 
    BeautifulSoup object for HTML parsing. Handles HTTP and URL-related errors gracefully.

    Parameters:
    ----------
    url : str
        The URL of the web page to fetch.
    timeout : float, optional
        The maximum time (in seconds) to wait for a response before timing out. Default is 100 seconds.

    Returns:
    -------
    BeautifulSoup or None
        A BeautifulSoup object containing the parsed HTML content if successful,
        otherwise None if an error occurs.
    '''

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0'
    }

    req = Request(url, headers=headers)

    try:
        response = urlopen(req, timeout=timeout)
        body = response.read().decode('utf-8')
        soup = BeautifulSoup(body)
        return soup
    except HTTPError as http_err:
        print(f"[HTTP ERROR] {url} returned status {http_err.code}: {http_err}")
    except URLError as url_err:
        print(f"[URL ERROR] Could not access {url}: {url_err}")
    
    return None

def get_links_by_keyword(soup:BeautifulSoup, keyword:str) -> list[str]:
    '''
    Extracts and returns all <a> tag hyperlinks that contain a specific keyword in their 'href'.

    This function searches through all anchor tags in the provided BeautifulSoup object
    and collects full URLs whose 'href' attribute includes the given keyword.

    Parameters:
    ----------
    soup : BeautifulSoup
        A BeautifulSoup object representing the parsed HTML of a web page.
    keyword : str
        The keyword to search for within the 'href' attributes of <a> tags.

    Returns:
    -------
    list[str]
        A list of string URLs where each URL contains the specified keyword.
    '''

    collected_links = list()

    # Loop through all link tags 
    for a_tag in soup.find_all('a', recursive=True, href=True):
        # Exclude if keyword is not present in href
        if keyword not in a_tag['href']:
            continue
        collected_links.append(a_tag['href'])

    return collected_links

def parse_program_html(soup:BeautifulSoup) -> str:
      '''
    Extracts and returns the HTML string of the section containing program requirements 
    from a McGill program homepage.

    This function searches through the provided BeautifulSoup object and locates the portion 
    of the HTML that contains program requirements, such as prerequisites, required courses, 
    complementary courses, and advising notes. It assumes the program requirements are 
    encapsulated within a specific HTML tag or identifiable structure (e.g., a <div> with a 
    known class or ID).

    Parameters:
    ----------
    soup : BeautifulSoup
        A BeautifulSoup object representing the parsed HTML of a McGill program webpage.

    Returns:
    -------
    str
        A string containing the HTML of the program requirements section. 
        Returns an empty string if the section is not found.
    '''
    
    program_tag = soup.find("div", attrs={"id"="programoverviewtextcontainer", "class"="page_content tab_content"})

    if not program_tag:
        raise ValueError("Given link does not contain required information")

    return program_tag.get_text()
