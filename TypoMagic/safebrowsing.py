import datetime as DT
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

    try:
        f = open('api_count.txt', 'r+')
        line = f.readline()
        date = line[:19]
        length =  len(line)
        value = int(line[20:length])
        now = DT.datetime.now()
        then = DT.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        delta = now - then
        if (value < 10000) and ((now - then).seconds < 86400):
            value += 1
            f = open('api_count.txt', 'w')
            f.write(date + "=" + str(value))		
        elif ((now - then).seconds > 86400): # If the delta is more than 24 hours reset the counter
            today = DT.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(str(today) + "=1")		
        else: # API limit reached
            return("")
        f.close()
    except:
        """Safe browsing count does not exist or an error of some sort
        In this case then write the current time plus the API count e.g.
        2014-01-05 14:47:25=0
        """
        f = open('api_count.txt', 'w')
        today = DT.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(str(today) + "=1")
        f.close()
		
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
		
    """This code block will deal with Google Safe Browsing API abuse.
	It will check the current datetime and compare this against the api_count.txt value.
	If the count is more than 10K and the datetime is with a 24 time frame then the function will just return with no results.
    """
    try:
        f = open('api_count.txt', 'r+')
        line = f.readline()
        date = line[:19]
        length =  len(line)
        value = int(line[20:length])
        now = DT.datetime.now()
        then = DT.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        delta = now - then
        if (value < 10000) and ((now - then).seconds < 86400):
            value += 1
            f = open('api_count.txt', 'w')
            f.write(date + "=" + str(value))		
        elif ((now - then).seconds > 86400): # If the delta is more than 24 hours reset the counter
            today = DT.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(str(today) + "=1")		
        else: # API limit reached
            return("")
        f.close()
    except:
        """Safe browsing count does not exist or an error of some sort
        In this case then write the current time plus the API count e.g.
        2014-01-05 14:47:25=0
        """
        f = open('api_count.txt', 'w')
        today = DT.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(str(today) + "=1")
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