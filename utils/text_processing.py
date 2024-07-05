import mwparserfromhell
from bs4 import BeautifulSoup, Comment


def read_wikitext(file_path):
    """Reads the content of a text file containing wikitext."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def parse_wikitext_to_clean_text(wikitext):
    """Parses wikitext and returns clean text."""
    parsed = mwparserfromhell.parse(wikitext)
    return parsed.strip_code().strip()


def parse_database_text(text):
    """Process the text extracted from the database."""
    text = strip_html_tags(text)
    return text.replace('_', ' ').replace('|', ', ')


def strip_html_tags(text):
    """Remove HTML tags, unwanted attributes, and preserve essential text."""
    soup = BeautifulSoup(text, "html.parser")

    # Remove comments and script/style elements
    for element in soup(text=lambda text: isinstance(text, Comment)):
        element.extract()
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # Remove all unwanted attributes from tags
    for tag in soup.find_all(True):
        tag.attrs = {}

    # Remove specific unwanted tags but preserve their content
    for tag in soup.find_all(["div", "span", "table", "tr", "td", "th", "big", "u"]):
        tag.unwrap()

    # Convert list items to plain text
    for li in soup.find_all('li'):
        li.insert_before('\n* ')
        li.unwrap()

    # Get the cleaned text
    cleaned_text = soup.get_text(separator=' ', strip=True)

    return cleaned_text.strip()


def extract_text_between_big_tags(text):
    """Extract text between the first pair of <big> and </big> tags"""
    soup = BeautifulSoup(text, 'html.parser')
    big_tag = soup.find('big')
    if big_tag:
        next_sibling = big_tag.find_next_sibling()
        extracted_text = big_tag.get_text()
        while next_sibling and next_sibling.name != 'big':
            extracted_text += str(next_sibling)
            next_sibling = next_sibling.find_next_sibling()
        return extracted_text
    return text