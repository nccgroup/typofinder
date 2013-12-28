import http.client
from urllib import parse

def safebrowsingquery (query_hostname):
    """
    Performs a lookup against Google's Safe Browsing API and returns the result as HTML. Only the root HTTP URL is
    passed to Google.

    @param query_hostname: The hostname to check, e.g. for malware "exciteagainst.net"
    @return: An HTML string describing the suspected unsafe website (using Google's preferred phrasing) or the empty
    string if no warning is received from Google.
    """
    query_url = parse.quote("http://" + query_hostname + "/", safe='')

    connection = http.client.HTTPSConnection("sb-ssl.google.com")
    connection.request("GET","/safebrowsing/api/lookup?client=api&apikey=ABQIAAAAB3xQRt9EShpO-iyQX0WwGhSXHj4Ub9ljl4rIx6fxoRCWhDWoBg&appver=1.0&pver=3.0&url=" + query_url)
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
