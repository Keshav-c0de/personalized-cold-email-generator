from bs4 import BeautifulSoup

def extract_info(html_content: str) -> dict:
    info = {}

    soup = BeautifulSoup(html_content, 'html.parser')

    if soup:
        posts_elements = soup.find_all(attrs={"data-testid": "expandable-text-box"})
        lazy_column = soup.find(attrs={"data-testid": "lazy-column"})
        profile_name_elements = lazy_column.find("h2") if lazy_column else None
        profile_title_elements = lazy_column.find_all("p") if lazy_column else []

        clean_post_list = safe_extract_list(posts_elements)
        clear_title_text_list = safe_extract_list(profile_title_elements)
        clear_profile_name = safe_extract_string(profile_name_elements)


        info["profile_name"] = clear_profile_name
        info["profile_title"] = clear_title_text_list
        info["posts"] = clean_post_list

    return info


def safe_extract_string(soup_element):
    """Safely extracts text if the element exists, returns None if it doesn't."""
    return soup_element.get_text(strip=True) if soup_element else None

def safe_extract_list(soup_elements):
    """Safely extracts text from a list of elements, returns an empty list if none exist."""
    return [element.get_text(strip=True) for element in soup_elements] if soup_elements else []

