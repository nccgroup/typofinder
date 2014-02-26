import datetime as DT
import http.client
from urllib import parse

# globals
value = 0
longtermthen = DT.datetime.now()
now = DT.datetime.now()

def safebrowsingqueryv2(query_hostname, key):
    """
    Performs a lookup against Google's Safe Browsing API and returns the result as HTML. Only the root HTTP URL is
    passed to Google.

    To use the Google Safe Browsing API you must register for an API key.
    Obtain your API key here: https://developers.google.com/safe-browsing/key_signup

    You can find further information on Google Safe Browsing API here:
    https://developers.google.com/safe-browsing/

    @param query_hostname: The hostname to check, e.g. for malware "exciteagainst.net"
    @param key: The Google Safe Browsing Key.
    @return: An HTML string describing the suspected unsafe website (using Google's preferred phrasing) or the empty
    string if no warning is received from Google.
    """
    if key == "":
        # Return the same as a positive response string if the Safe Browsing API key is missing.
        return ""

    global now, value, longtermthen
    then = now
    now = DT.datetime.now()

    # Make sure the Google Safe Browsing API is not abused
    if (value < 10000) and ((now - then).seconds < 86400):
        value += 1
    elif (now - longtermthen).seconds > 86400:
        value = 0
        longtermthen = now
    else:
        return ""

    query_url = parse.quote("http://" + query_hostname, safe='')

    connection = http.client.HTTPSConnection("sb-ssl.google.com")
    connection.request("GET", "/safebrowsing/api/lookup?client=api&apikey=" + key + "&appver=1.0&pver=3.0&url=" + query_url)
    response = connection.getresponse()

    if response.getcode() == 200:
        body = "suspected " + response.read().decode('utf-8')
        title = ""

        if "phishing" in body:
            title += "Warning- Suspected phishing page. This page may be a forgery or imitation of another website, designed to trick users into sharing personal or financial information. Entering any personal information on this page may result in identity theft or other abuse. You can find out more about phishing from www.antiphishing.org."
        elif "malware" in body:
            title += "Warning- Visiting this web site may harm your computer. This page appears to contain malicious code that could be downloaded to your computer without your consent. You can learn more about harmful web content including viruses and other malicious code and how to protect your computer at StopBadware.org."

        return title
    elif response.getcode() == 204:
        return ""