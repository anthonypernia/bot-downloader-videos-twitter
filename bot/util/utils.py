"""utils functions"""
import pyshorteners


def shorten_link(url: str) -> str:
    """Shorten a link

    Args:
        url (str): url to shorten

    Returns:
        str: shortened url
    """
    shortener = pyshorteners.Shortener()
    short_url = shortener.tinyurl.short(url)
    return short_url
