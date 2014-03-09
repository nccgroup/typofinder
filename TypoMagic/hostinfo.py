#
# Typofinder for domain typo discovery
# 
# Released as open source by NCC Group Plc - http://www.nccgroup.com/
# 
# Developed by Ollie Whitehouse, ollie dot whitehouse at nccgroup dot com
#
# http://www.github.com/nccgroup/typofinder
#
# Released under AGPL see LICENSE for more information#
#

import dns.resolver
import pygeoip


class hostinfo(object):
    """Host information class"""

    A_type = dns.rdatatype.from_text('A')
    AAAA_type = dns.rdatatype.from_text('AAAA')

    def __init__(self):
        self._resolver = dns.resolver.Resolver()
        self._resolver.Timeout = 2.0
        self._resolver.lifetime = 2.0
        self._resolver.cache = dns.resolver.LRUCache()
        self._resolver.search = list() #Ensure no search suffixes
        self._gi = pygeoip.GeoIP('GeoIP.dat')
        self._giv6 = pygeoip.GeoIP('GeoIPv6.dat')

    def do_query(self, prefix, sHostname, rdatatype):
        try:
            if prefix:
                domainname = dns.name.from_text(prefix + '.' + sHostname, origin=dns.name.root)
            else:
                domainname = dns.name.from_text(sHostname, origin=dns.name.root)

            dnsAnswers = self._resolver.query(domainname, rdatatype)
            return dnsAnswers
        except dns.exception.Timeout:
            return None
        except dns.resolver.NoAnswer:
            return None
        except dns.resolver.NoNameservers:
            return None

    def getWWW(self, sHostname):
        return self.do_query('www', sHostname, self.A_type)

    def getWWWv6(self, sHostname):
        return self.do_query('www', sHostname, self.AAAA_type)

    def getM(self, sHostname):
        return self.do_query('m', sHostname, self.A_type)

    def getMv6(self, sHostname):
        return self.do_query('m', sHostname, self.AAAA_type)

    def getWEBMail(self, sHostname):
        return self.do_query('webmail', sHostname, self.A_type)

    def getWEBMailv6(self, sHostname):
        return self.do_query('webmail', sHostname, self.AAAA_type)

    def getMX(self, sHostname):
        # MX
        try:
            return self.do_query(None, sHostname, dns.rdatatype.from_text('MX'))
        except dns.resolver.NXDOMAIN:   #Special case, return None rather than throwing NXDOMAIN (TODO figure out why!)
            return None

    def getIPv4(self, sHostname):
        return self.do_query(None, sHostname, self.A_type)

    def getIPv6(self, sHostname):
        return self.do_query(None, sHostname, self.AAAA_type)

    def getGeobyIP(self, sIP):
        try:
            # Geo Location
            return self._gi.country_code_by_addr(sIP)
        except Exception:
            pass
    
    def getGeobyIPv6(self, sIP):
        try:
            # Geo Location
            return self._giv6.country_code_by_addr(sIP)
        except Exception:
            pass

    #
    # these are used by the v2 AJAX API
    #
    def getGeoImagebyIPv4new(self, sIP):
        try:
            countrycode = self.getGeobyIP(sIP)
            if countrycode:
                return "/flags/flags-iso/shiny/16/"+ countrycode + ".png"
        except Exception:
            pass
        return "/flags/flags-iso/shiny/16/_unknown.png"

    def getGeoImagebyIPv6new(self, sIP):
        try:
            countrycode = self.getGeobyIPv6(sIP)
            if countrycode:
                return "/flags/flags-iso/shiny/16/"+ countrycode + ".png"
        except Exception:
            pass
        return "/flags/flags-iso/shiny/16/_unknown.png"
