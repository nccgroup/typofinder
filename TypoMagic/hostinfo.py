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
    
    def getWWW(sHostname):
        # WWW
        try:
            dnsAnswers = dns.resolver.query("www." + sHostname, 'A')
            return dnsAnswers
        except dns.exception.Timeout:
            return None
        except dns.resolver.NoAnswer:
            return None
        except dns.resolver.NXDOMAIN:
            return None

    def getM(sHostname):
        # M
        try:
            dnsAnswers = dns.resolver.query("m." + sHostname, 'A')
            return dnsAnswers
        except dns.exception.Timeout:
            return None
        except dns.resolver.NoAnswer:
            return None
        except dns.resolver.NXDOMAIN:
            return None

    def getWEBMail(sHostname):
        # webmail
        try:
            dnsAnswers = dns.resolver.query("webmail." + sHostname, 'A')
            return dnsAnswers
        except dns.exception.Timeout:
            return None
        except dns.resolver.NoAnswer:
            return None
        except dns.resolver.NXDOMAIN:
            return None

    def getMX(sHostname):
        # MX
        try:
            dnsAnswers = dns.resolver.query(sHostname, 'MX')
            return dnsAnswers
        except dns.exception.Timeout:
            return None
        except dns.resolver.NoAnswer:
            return None
        except dns.resolver.NXDOMAIN:
            return None

    def getIPv4(sHostname):
        # IPv4
        try:  
            dnsAnswers = dns.resolver.query(sHostname, 'A')
            return dnsAnswers
        except dns.exception.Timeout:
            return None
        except dns.resolver.NoAnswer:
            return None

    def getIPv6(sHostname):
        # IPv6
        try:       
            dnsAnswers = dns.resolver.query(sHostname, 'AAAA')
            return dnsAnswers
        except dns.exception.Timeout:
            return None
        except dns.resolver.NoAnswer:
            return None

    def getGeobyIP(sIP):
        try:
            # Geo Location    
            gi = pygeoip.GeoIP('./GeoIP.dat')
            #print(gi.country_code_by_addr(sIP))
            return gi.country_code_by_addr(sIP)
        except Exception as e:
            #print("Error doing getGeoIP ")
            pass

    def getGeobyHostname(sHostname):
        try:
            # Geo Location    
            gi = pygeoip.GeoIP('./GeoIP.dat')
            #print(gi.country_code_by_name(sHostname))
            return gi.country_code_by_name(sHostname)
        except Exception as e:
            #print("Error doing getGeoHostname ")
            pass

    def getGeoImagebyIP(sIP):
        try:
            return "<img src=\"/flags/flags-iso/shiny/16/"+ hostinfo.getGeobyIP(sIP)+".png\" alt=\"" + hostinfo.getGeobyIP(sIP) + "\">"
        except Exception as e:
            #print("Error doing getGeoImagebyIP ")
            return "<img src=\"/flags/flags-iso/shiny/16/_unknown.png\">"

    def getGeoImagebyHostname(sHostname):
        try:
            return "<img src=\"/flags/flags-iso/shiny/16/"+ hostinfo.getGeobyHostname(sHostname)+".png\" alt=\"" + hostinfo.getGeobyHostname(sHostname) + "\">"
        except Exception as e:
            #print("Error doing getGeoImagebyHostname ")
            return "<img src=\"/flags/flags-iso/shiny/16/_unknown.png\">"
            
        