Domain typo finder
======================

Typofinder for domain typo discovery

Released as open source by NCC Group Plc - http://www.nccgroup.com/

Developed by:
* Ollie Whitehouse, ollie dot whitehouse at nccgroup dot com
* Stephen Tomkinson, @neonbunny9 on twitter
* Matt Summers, matt dot summers at nccgroup dot com

https://github.com/nccgroup/typofinder

Released under AGPL see LICENSE for more information

Want to give it a go?
-------------
A sample deployment can be found here:
* https://labs.nccgroup.com/typofinder/

Development Wiki
-------------
Some rough notes on the v2 architecture:
* https://github.com/nccgroup/typofinder/wiki

Features
-------------
* Domain to IP
* MX records
* A and AAAA
* www address records
* webmail address records
* m address records
* A keyboard map template system (currently UK supplied)
* Geographic IP to flag
* Google safe browsing integration
* Bit flipping/squatting - http://dinaburg.org/bitsquatting.html
* Homoglyph attack identification
* Whois
 
Dependencies - server
-------------
* Python (3.3)
* dnspython3 (1.11.1)
* pygeoip (0.3.1)
* publicsuffix (1.0.5)

Dependencies - client
-------------
* Python (3.3)
* simplejson
* requests
* BeautifulSoup (4)
* html5lib

What it does
-------------
* remove characters from the supplied domain
* duplicate characters in the supplied domain
* replace characters with adjacent keyboard characters depending on keyboard map supplied
* swap the global TLD for each of the current valid TLDs lists at - http://data.iana.org/TLD/tlds-alpha-by-domain.txt
* flip bits in the legit domain to detect the bitsquatting attacks
* swaps characters with similar looking characters to find homoglyph attacks
* checks websites against Google's Safe Browsing API<sup>1</sup>

Usage
-------------
* Launch in TypoMagic directory
* Connect to http://127.0.0.1:801/
* Follow prompts

Updating Data Sources
-------------
The included updatedatasources.py script can be used to ensure that the program is using the latest 3rd party data.
Please be considerate of the data providers and use this script sparingly.

Google Safe Browsing API Key
-------------
To use the Google Safe Browsing API you must register for an API key.
Obtain your API key here: https://developers.google.com/safe-browsing/key_signup
	
You can find further information on Google Safe Browsing API here:
https://developers.google.com/safe-browsing/

If you have a Google Safe Browsing API you can enter this at the command line e.g.
python TypoMagic.py -k <API>

Alternately you can place your API in the KEY parameter in TypoMagic.py.

<sup>1</sup> Google works to provide the most accurate and up-to-date phishing and malware information.
However, it cannot guarantee that its information is comprehensive and error-free: some risky sites may not be
identified, and some safe sites may be identified in error.
