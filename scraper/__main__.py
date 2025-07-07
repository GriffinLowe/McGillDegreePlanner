from azure.storage.blob import BlobServiceClient
import os
import io
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import json

# Global vars
BASE_URL = 'https://coursecatalogue.mcgill.ca/en/undergraduate/'
SCIENCE_KEYWORD = 'undergraduate/science/programs'
ARTS_KEYWORD = 'undergraduate/arts/programs'
AGRICULTURE_KEYWORD = 'undergraduate/agri-env-sci/programs'
ENVIRONMENT_KEYWORD = 'undergraduate/environment/programs'
ENGINEERING_KEYWORD = 'undergraduate/engineering/programs'
ART_SCI_KEYWORD = 'undergraduate/arts-science/programs'
EDUCATION_KEYWORD = 'undergraduate/education/programs'
MANAGEMENT_KEYWORD = 'undergraduate/management/programs'
MUSIC_KEYWORD = 'undergraduate/music/programs'


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
        soup = BeautifulSoup(body, 'html.parser')
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
    
    program_tag = soup.find("div", {"id": "programoverviewtextcontainer"})


    if not program_tag:
        raise ValueError("Given link does not contain required information")

    return program_tag.get_text()

def upload_blob_stream(blob_service_client: BlobServiceClient, container_name: str, source_url: str, source_html: str, blob_name: str):
    """
    Uploads HTML content and its source URL as a JSON object to Azure Blob Storage using an in-memory byte stream.

    This function is intended for single-use or internal workflows, where scraped HTML data and its originating
    link need to be persisted in the cloud. The function creates a JSON object containing the source URL and
    HTML content, writes it to an in-memory byte stream, and uploads it to the specified blob container.
a
    Parameters
    ----------
    blob_service_client : BlobServiceClient
        An authenticated instance of the Azure BlobServiceClient.
    container_name : str
        The name of the Azure blob container to upload to.
    source_url : str
        The URL from which the HTML content was retrieved.
    source_html : str
        The raw HTML string content to store.
    blob_name : str
        The name of the blob (file) to create or overwrite in the container.

    Returns
    -------
    None
    """
    
    # Create JSON string:
    data = {"link": source_url,
            "html": source_html}
    json_data = json.dumps(data)

    # Establish connection to Azure blob storage: 
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Upload to blob store
    input_stream = io.BytesIO(json_data.encode('utf-8'))
    blob_client.upload_blob(input_stream, blob_type="BlockBlob", overwrite=True)

def main():

    print("entered main")

    base_soup = get_page(BASE_URL)

    # Get program links by department
    science_links = get_links_by_keyword(base_soup, SCIENCE_KEYWORD)
    arts_links = get_links_by_keyword(base_soup, ARTS_KEYWORD)
    agri_links = get_links_by_keyword(base_soup, AGRICULTURE_KEYWORD)
    environment_links = get_links_by_keyword(base_soup, ENVIRONMENT_KEYWORD)
    engineering_links = get_links_by_keyword(base_soup, ENGINEERING_KEYWORD)
    art_sci_links = get_links_by_keyword(base_soup, ART_SCI_KEYWORD)
    education_links = get_links_by_keyword(base_soup, EDUCATION_KEYWORD)
    management_links = get_links_by_keyword(base_soup, MANAGEMENT_KEYWORD)
    music_links = get_links_by_keyword(base_soup, MUSIC_KEYWORD)

    # Connection to blob storage:
    blob_client = BlobServiceClient(os.getenv('SAS BLOB STORAGE TOKEN'))

    # Define departments and corresponding link lists
    departments = {
        "science/programs": science_links,
        "arts/programs": arts_links,
        "agri-env-sci/programs": agri_links,
        "environment/programs": environment_links,
        "engineering/programs": engineering_links,
        "arts-science/programs": art_sci_links,
        "education/programs": education_links,
        "management/programs": management_links,
        "music/programs": music_links
    }

    print("upload beginning")

    # Upload parsed HTML from each department's program links to blob storage
    for keyword, links in departments.items():
        for link in links:
            try:
                soup = get_page(BASE_URL + link[18:])
                print("Soup found")

                html = parse_program_html(soup)
                print("html parsed")
                blob_name = link[18:].replace('/', '.')
                upload_blob_stream(blob_client, "rawscrape", BASE_URL + link[18:], html, blob_name)
                print(link)
            except Exception as e:
                print(f"[ERROR] Failed to process {link}: {e}")

if __name__ == "__main__":
    main()
