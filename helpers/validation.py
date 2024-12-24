import re
import validators

def extract_and_validate_url(message: str) -> str | None:
    url_pattern = re.compile(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b(?:/[^\s]*)?')
    match = url_pattern.search(message)

    if match:
        url = match.group(0)
        if validators.url(f'http://{url}'):
            return url
    return None
