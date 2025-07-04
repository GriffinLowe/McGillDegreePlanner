from utils import get_page, get_links_by_keyword, parse_program_html
from cloud_utils import upload_blob_stream
from azure.storage.blob import BlobServiceClient
import config as c
import os

def main():

    base_soup = get_page(c.BASE_URL)

    # Get program links by department
    science_links = get_links_by_keyword(base_soup, c.SCIENCE_KEYWORD)
    arts_links = get_links_by_keyword(base_soup, c.ARTS_KEYWORD)
    agri_links = get_links_by_keyword(base_soup, c.AGRICULTURE_KEYWORD)
    environment_links = get_links_by_keyword(base_soup, c.ENVIRONMENT_KEYWORD)
    engineering_links = get_links_by_keyword(base_soup, c.ENGINEERING_KEYWORD)
    art_sci_links = get_links_by_keyword(base_soup, c.ART_SCI_KEYWORD)
    education_links = get_links_by_keyword(base_soup, c.EDUCATION_KEYWORD)
    management_links = get_links_by_keyword(base_soup, c.MANAGEMENT_KEYWORD)
    music_links = get_links_by_keyword(base_soup, c.MUSIC_KEYWORD)

    # Connection to blob storage:
    blob_client = BlobServiceClient(os.getenv('SAS ACCOUNT URL'))

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

    # Upload parsed HTML from each department's program links to blob storage
    for keyword, links in departments.items():
        for link in links:
            try:
                soup = get_page(link)
                html = parse_program_html(soup)
                blob_name = link[link.find(keyword):].replace('/', '.')
                upload_blob_stream(blob_client, "rawscrape", link, html, blob_name)
            except Exception as e:
                print(f"[ERROR] Failed to process {link}: {e}")

if __name__ == "__main__":
    main()
