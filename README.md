Domain typo finder
======================

Typofinder for domain typo discovery

Released as open source by NCC Group Plc - http://www.nccgroup.com/

Developed by Ollie Whitehouse, ollie dot whitehouse at nccgroup dot com

https://github.com/nccgroup/typofinder

Released under AGPL see LICENSE for more information

Features
-------------
* Domain to IP
* MX records
* A and AAAA
* www address records
* webmail address records
* m address records
* A keyboard map template system (currently UK supplied)

Dependencies
-------------
* dnspython (1.11.1)
* pygeoip (0.3.0)

What it does
-------------
* remove characters from the supplied domain
* duplicate characters in the suppled domain
* replace characters with adjacent keyboard characters depending on keyboard map supplied
* swap the global TLD for each of the current valid TLDs list at - http://data.iana.org/TLD/tlds-alpha-by-domain.txt
* checks web sites against Google's Safe Browsing API<sup>1</sup>

Usage
-------------
* Launch in TypoMagic directory
* Connect to http://127.0.0.1:801
* Follow prompts

If you would like to use the Google Safe Browsing check your must first request an API key and place this in "apikey" parameter in safebrowsing.py

Obtain your API key here: https://developers.google.com/safe-browsing/key_signup

You can find further information on Google Safe Browsing API here: https://developers.google.com/safe-browsing/

<sup>1</sup> Google works to provide the most accurate and up-to-date phishing and malware information.
However, it cannot guarantee that its information is comprehensive and error-free: some risky sites may not be
identified, and some safe sites may be identified in error.
