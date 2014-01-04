import http.client
from urllib import parse

def safebrowsingquery (query_hostname, key):
    """
    Performs a lookup against Google's Safe Browsing API and returns the result as HTML. Only the root HTTP URL is
    passed to Google.

    To use the Google Safe Browsing API you must register for an API key.
	Obtain your API key here: https://developers.google.com/safe-browsing/key_signup
	
	You can find further information on Google Safe Browsing API here:
	https://developers.google.com/safe-browsing/
	
    @param query_hostname: The hostname to check, e.g. for malware "exciteagainst.net"
    @return: An HTML string describing the suspected unsafe website (using Google's preferred phrasing) or the empty
    string if no warning is received from Google.
    """
    if key == "":
        # Return the same as a positive response string if the Safe Browsing API key is missing.
        return ("")
		
    # Build the query URL to send to Google Safe Browsing
    # TODO: Put some intelligence around this function because you rely on the user to enter a URL without the protocol, which BTW you don't actually need to send to GSB
    query_url = parse.quote("http://" + query_hostname, safe='')

    connection = http.client.HTTPSConnection("sb-ssl.google.com")
    connection.request("GET","/safebrowsing/api/lookup?client=api&apikey=" + key + "&appver=1.0&pver=3.0&url=" + query_url)
    response = connection.getresponse()

    if response.getcode() == 200:
        body = "suspected " + response.read().decode('utf-8')
        title = ""

        if "phishing" in body:
            title += "Warning- Suspected phishing page. This page may be a forgery or imitation of another website, designed to trick users into sharing personal or financial information. Entering any personal information on this page may result in identity theft or other abuse. You can find out more about phishing from www.antiphishing.org."
        elif "malware" in body:
            title += "Warning- Visiting this web site may harm your computer. This page appears to contain malicious code that could be downloaded to your computer without your consent. You can learn more about harmful web content including viruses and other malicious code and how to protect your computer at StopBadware.org."

        return "<b style='color:red' title='" + title + "'>" + body + "</b>" 
    elif response.getcode() == 204:
        return ""

def safebrowsingqueryv2 (query_hostname, key):
    """
    Performs a lookup against Google's Safe Browsing API and returns the result as HTML. Only the root HTTP URL is
    passed to Google.

    @param query_hostname: The hostname to check, e.g. for malware "exciteagainst.net"
    @return: An HTML string describing the suspected unsafe website (using Google's preferred phrasing) or the empty
    string if no warning is received from Google.
    """
    if key == "":
        # Return the same as a positive response string if the Safe Browsing API key is missing.
        return ("")

    # Make sure the Google Safe Browsing API is not abused
    try:
        f = open('api_count.txt', 'r+')
        line = f.readline()
        value = int(line)
        if value < 10000:
            value += 1
            f = open('api_count.txt', 'w')
            f.write(str(value))		
        else:
            # API limit reached, don't make any more calls
            return ("")
        f.close()
    except:
        # Safe browsing count does not exist, set the value to one and continue
        f = open('api_count.txt', 'w')
        f.write("1")
        f.close()
		
    query_url = parse.quote("http://" + query_hostname, safe='')

    connection = http.client.HTTPSConnection("sb-ssl.google.com")
    connection.request("GET","/safebrowsing/api/lookup?client=api&apikey=" + key + "&appver=1.0&pver=3.0&url=" + query_url)
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