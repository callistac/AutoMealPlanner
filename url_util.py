'''
Modified version of the util.py file provided in pa2 to work on allrecipes.com.
Also used for scraping the Hyde Park Produce site. Global variables which are
defined before the is_url_ok_to_follow function are only applied to the
allrecipes.com crawling, as the "ok to follow" check is unnecessary for the Hyde
Park Produce scraping.

Modified by: Melissa Merz
'''


import urllib.parse
import requests
import os
import bs4


def get_request(url):
    '''
    Open a connection to the specified URL and if successful
    read the data.

    Inputs:
        url: must be an absolute URL

    Outputs:
        request object or None

    Examples:
        get_request("http://www.cs.uchicago.edu")
    '''

    if is_absolute_url(url):
        try:
            r = requests.get(url)
            if r.status_code == 404 or r.status_code == 403:
                r = None
        except Exception:
            # fail on any kind of error
            r = None
    else:
        r = None

    return r


def read_request(request):
    '''
    Return data from request object.  Returns result or "" if the read
    fails..
    '''

    try:
        return request.text
    except Exception:
        print("read failed: " + request.url)
        return ""


def get_request_url(request):
    '''
    Extract true URL from the request
    '''
    return request.url


def is_absolute_url(url):
    '''
    Is url an absolute URL?
    '''
    if url == "":
        return False
    return urllib.parse.urlparse(url).netloc != ""


def remove_fragment(url):
    '''remove the fragment from a url'''

    (url, frag) = urllib.parse.urldefrag(url)
    return url


def convert_if_relative_url(current_url, new_url):
    '''
    Attempt to determine whether new_url is a relative URL and if so,
    use current_url to determine the path and create a new absolute
    URL.  Will add the protocol, if that is all that is missing.

    Inputs:
        current_url: absolute URL
        new_url:

    Outputs:
        new absolute URL or None, if cannot determine that
        new_url is a relative URL.

    Examples:
        convert_if_relative_url("http://cs.uchicago.edu", "pa/pa1.html") yields
            'http://cs.uchicago.edu/pa/pa1.html'

        convert_if_relative_url("http://cs.uchicago.edu", "foo.edu/pa.html")
            yields 'http://foo.edu/pa.html'
    '''
    if new_url == "" or not is_absolute_url(current_url):
        return None

    if is_absolute_url(new_url):
        return new_url

    parsed_url = urllib.parse.urlparse(new_url)
    path_parts = parsed_url.path.split("/")

    if len(path_parts) == 0:
        return None

    ext = path_parts[0][-4:]
    if ext in [".edu", ".org", ".com", ".net"]:
        return "http://" + new_url
    elif new_url[:3] == "www":
        return "http://" + new_path
    else:
        return urllib.parse.urljoin(current_url, new_url)


#the following are all bad page extensions, as they lead off into non-recipe
#areas of the website, they should thus be ignore by the crawler
ACCOUNT = ("https://www.allrecipes.com/account")
LEN_ACCOUNT = len(ACCOUNT)

COOK = ("https://www.allrecipes.com/cook")
LEN_COOK = len(COOK)

VIDEO = ("https://www.allrecipes.com/video")
LEN_VIDEO = len(VIDEO)

ARTICLE = ("https://www.allrecipes.com/article")
LEN_ARTICLE = len(ARTICLE)

GALLERY = ("https://www.allrecipes.com/gallery")
LEN_GALLERY = len(GALLERY)

REVIEWS = ("/reviews/")

ARTICLE = ("/article/")

PHOTOS = ("/photos/")

PRINT = ("/print/")

BREAD = ("/bread/")

DESSERTS = ("/desserts/")

DRINKS = ("/drinks/")

HOLIDAYS = ("/holidays-and-events/")

#the following aren't categories on allrecipes.com, so it's easier to exclude
#them here by examining the urls and just not crawling to them
PICKLES = ("pickle")

INSTANT_POT = ("instant-pot")

AIR_FRYER = ("air-fryer")


def is_url_ok_to_follow(url, limiting_domain):
    '''
    Inputs:
        url: absolute URL
        limiting domain: domain name

    Outputs:
        Returns True if the protocol for the URL is HTTP(s), the domain
        is in the limiting domain, and the path is either a directory
        or a file that has no extension or ends in .html. URLs
        that include an "@" are not OK to follow.

    Examples:
        is_url_ok_to_follow("http://cs.uchicago.edu/pa/pa1", "cs.uchicago.edu")
            yields True

        is_url_ok_to_follow("http://cs.cornell.edu/pa/pa1", "cs.uchicago.edu")
            yields False
    '''

    if "mailto:" in url:
        return False

    if "@" in url:
        return False

    if url[:LEN_ACCOUNT] == ACCOUNT:
        return False

    if url[:LEN_COOK] == COOK:
        return False

    if url[:LEN_VIDEO] == VIDEO:
        return False

    if url[:LEN_ARTICLE] == ARTICLE:
        return False

    if url[:LEN_GALLERY] == GALLERY:
        return False

    if REVIEWS in url:
        return False

    if ARTICLE in url:
        return False

    if PRINT in url:
        return False

    if DRINKS in url:
        return False

    if DESSERTS in url:
        return False

    if BREAD in url:
        return False

    if HOLIDAYS in url:
        return False

    if PICKLES in url:
        return False

    if INSTANT_POT in url:
        return False

    if AIR_FRYER in url:
        return False

    if PHOTOS in url:
        return False

    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.scheme != "http" and parsed_url.scheme != "https":
        return False

    if parsed_url.netloc == "":
        return False

    if parsed_url.fragment != "":
        return False

    if parsed_url.query != "":
        return False

    loc = parsed_url.netloc
    ld = len(limiting_domain)
    trunc_loc = loc[-(ld+1):]
    if not (limiting_domain == loc or (trunc_loc == "." + limiting_domain)):
        return False

    # does it have the right extension
    (filename, ext) = os.path.splitext(parsed_url.path)
    return (ext == "" or ext == ".html")
