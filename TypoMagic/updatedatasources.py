import urllib.request
import os
import gzip

def ungzip(in_file, out_file):
    with gzip.open(in_file) as in_data:
        with open(out_file, "wb") as out_file:
            out_file.write(in_data.read())
    os.remove(in_file)

try:
    os.makedirs("datasources")
except OSError:
    #It probably already exists, carry on
    pass
print('.', end='', flush=True)

urllib.request.urlretrieve("http://www.nirsoft.net/whois-servers.txt", "datasources/whois-servers.txt")
print('.', end='', flush=True)

urllib.request.urlretrieve("https://data.iana.org/TLD/tlds-alpha-by-domain.txt", "datasources/tlds-alpha-by-domain.txt")
print('.', end='', flush=True)

urllib.request.urlretrieve("http://opengeocode.org/download/countrynames.txt", "datasources/countrynames.txt")
print('.', end='', flush=True)

urllib.request.urlretrieve("http://www.unicode.org/Public/security/latest/confusables.txt", "datasources/confusables.txt")
print('.', end='', flush=True)

urllib.request.urlretrieve("http://publicsuffix.org/list/effective_tld_names.dat", "datasources/effective_tld_names.dat")
print('.', end='', flush=True)

urllib.request.urlretrieve("http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz", "datasources/GeoIP.dat.gz")
ungzip("datasources/GeoIP.dat.gz", "datasources/GeoIP.dat")
print('.', end='', flush=True)

urllib.request.urlretrieve("http://geolite.maxmind.com/download/geoip/database/GeoIPv6.dat.gz", "datasources/GeoIPv6.dat.gz")
ungzip("datasources/GeoIPv6.dat.gz", "datasources/GeoIPv6.dat")
print(' Done')