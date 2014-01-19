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

import argparse
from datetime import timedelta, date
import sys
import time
import socket
import http.server
import urllib
import traceback
from os import curdir, sep
from socketserver import ThreadingMixIn
import json

import dns.resolver

import typogen
import hostinfo
from objtypo import objtypo
import safebrowsing
from whois import ourwhois

_hostinfo = hostinfo.hostinfo()
_typogen = typogen.typogen()
KEY = ''

# v2 AJAX API
def handleHostAJAX(sDomain):
    typo = objtypo()
    
    typo.strDomain = sDomain
    
    # IP address for domain
    try:
        for hostData in _hostinfo.getIPv4(sDomain):
            typo.IPv4Address.append(hostData.address)
    except dns.resolver.NXDOMAIN:
        #Shortcut - If the domain query results in an NXDOMAIN, don't bother looking for subdomains.
        return typo
    except:
        pass

    try:
        for hostData in _hostinfo.getIPv6(sDomain):
            typo.IPV6Address.append(hostData.address)
    except:
        pass

    # MX
    try:
        for hostData in _hostinfo.getMX(sDomain):
            typo.aMX.append(str(hostData.exchange).strip("."))

            for hostDataInnerv4 in _hostinfo.getIPv4(str(hostData.exchange).strip(".")):
                if str(hostData.exchange).strip(".") in typo.aMXIPv4:
                    typo.aMXIPv4[str(hostData.exchange).strip(".")].append(hostDataInnerv4.address)
                else:
                    typo.aMXIPv4[str(hostData.exchange).strip(".")] = [hostDataInnerv4.address]

            for hostDataInnerv6 in _hostinfo.getIPv6(str(hostData.exchange).strip(".")):
                if str(hostData.exchange).strip(".") in typo.aMXIPv6:
                    typo.aMXIPv6[str(hostData.exchange).strip(".")].append(hostDataInnerv6.address)
                else:
                    typo.aMXIPv6[str(hostData.exchange).strip(".")] = [hostDataInnerv6.address]
    except:
        pass


    # Safe Browsing
    try:
        typo.SafeBrowsing = safebrowsing.safebrowsingqueryv2("www." + sDomain, KEY)
        pass
    except:
        pass

    # WWW
    try:
        for hostData in _hostinfo.getWWW(sDomain):
            typo.wwwv4.append(hostData.address)
    except:
        pass

    try:
        for hostData in _hostinfo.getWWWv6(sDomain):
            typo.wwwv6.append(hostData.address)
    except:
        pass

    # WebMail
    try:
        for hostData in _hostinfo.getWEBMail(sDomain):
            typo.webmailv4.append(hostData.address)
    except:
        pass

    try:
        for hostData in _hostinfo.getWEBMailv6(sDomain):
            typo.webmailv6.append(hostData.address)
    except:
        pass
    
    # M
    try:
        for hostData in _hostinfo.getM(sDomain):
            typo.mv4.append(hostData.address)
    except:
        pass

    try:
        for hostData in _hostinfo.getMv6(sDomain):
            typo.mv6.append(hostData.address)
    except:
        pass

    return typo

class MyHandler(http.server.BaseHTTPRequestHandler):

    def output(self, outputString):
        self.wfile.write(outputString.encode('utf-8'))

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_POST(self):
        """Respond to a POST request."""

        try:
            # v2 AJAX API generate typo domains
            if self.path.endswith("typov2.ncc"):
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
       
                length = int(self.headers['Content-Length'])
                post_data = urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'))
                print("[i] " + str(post_data))
                strHost = str(post_data['host'])[2:-2]

                # option checking
                bTLD = 'tld' in post_data
                bTypos = 'typos' in post_data
                try:
                     iTypoIntensity = int(post_data['typoamount'][0])
                except:
                     iTypoIntensity = 100

                bBitFlip = 'bitflip' in post_data

                # stupid user
                if(bTypos == False and bTLD == False and bBitFlip == False):
                     print("[i] No typos to process for " + strHost + " due to user option")
                     # this will cause an error in the JavaScript client which is relied upon
                     self.output("[!] No typos for " + strHost) 
                     return    

                # domain name validation
                if _typogen.is_domain_valid(strHost):
                    print("[i] Processing typos for " + strHost) 
                    lstTypos = _typogen.generatetyposv2(strHost, "gb", bTypos, iTypoIntensity, bTLD, bBitFlip)
                    if lstTypos is not None:
                        self.output(json.dumps([strTypoHost for strTypoHost in lstTypos]))
                    else:
                        # this will cause an error in the JavaScript client which is relied upon
                        self.output("[!] No typos for " + strHost) 
                        print("[!] No typos for " + strHost)   

                    print("[i] Processed typos for " + strHost)   
                    return
                else:
                    # this will cause an error in the JavaScript client which is relied upon
                    self.output("[!] Invalid domain " + strHost)  
                    print("[i] Invalid domain " + strHost)    
                    return
            # v2 AJAX API - get basic information for a domain      
            elif self.path.endswith("entity.ncc"):
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                length = int(self.headers['Content-Length'])
                post_data = urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'))
                strHost = str(post_data['host'])[2:-2]
                try:
                    objFoo = handleHostAJAX(strHost)
                    self.output(json.dumps(objFoo.reprJSON()))
                except dns.resolver.NXDOMAIN:
                    pass
        except:
            print(sys.exc_info())
            traceback.print_exc(file=sys.stdout)
            pass
              
        return

    def output_file(self, path, mime_type):
        """
        Sends the contents of the given file with the given "Content-type" header.

        @param path: The path to the file to send.
        @param mime_type: The content type.
        @raise IOError: If a path traversal is attempted.
        """
        if '..' in path:
            raise IOError
        else:
            with open(path, "rb") as f:
                self.send_response(200)
                self.send_header('Content-type',mime_type)
                self.end_headers()
                self.wfile.write(f.read())

    def do_GET(self):
        """Respond to a GET request."""

        try:
            if self.path.endswith("/"):
                self.output_file(curdir + sep + "index.html", 'text/html')
                return
            elif self.path.endswith(".html"):
                self.output_file(curdir + sep + self.path, 'text/html')
                return
            elif self.path.endswith(".css"):
                self.output_file(curdir + sep + self.path, 'text/css')
                return
            elif self.path.endswith(".js"):
                self.output_file(curdir + sep + self.path, 'application/javascript')
                return
            elif self.path.endswith(".map"):
                self.output_file(curdir + sep + self.path, 'application/json')
                return
            elif self.path.endswith(".ico"):
                self.output_file(curdir + sep + self.path, 'image/x-icon')
                return
            elif self.path.endswith(".png") and self.path.find("..") != 0:
                f = open(curdir + sep + self.path, "rb") 
                self.send_response(200)

                month = timedelta(days=30)
                futuredate = date.today() + month
                self.send_header('Expires',futuredate.strftime('%a, %d %b %Y %H:%M:%S GMT'))
                self.send_header('Content-type','image/png')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
            # v2 REST API - get geo for an IPv4
            elif "geov4.ncc" in self.path:
                lastSlash = self.path.rfind("/")
                strIP = self.path[lastSlash + 1:]
                strIMG = _hostinfo.getGeoImagebyIPv4new(strIP)

                f = open(curdir + sep + strIMG, "rb") 
                self.send_response(200)

                month = timedelta(days=30)
                futuredate = date.today() + month
                self.send_header('Expires',futuredate.strftime('%a, %d %b %Y %H:%M:%S GMT'))
                self.send_header('Content-type','image/png')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()


                #print("[-" + args.base + "/" + strIMG)

                #self.send_response(301)
                #self.send_header("Location", strIMG)
                #self.end_headers()
                #self.output("")
            # v2 REST API - get geo for an IPv6
            elif "geov6.ncc" in self.path:
                lastSlash = self.path.rfind("/")
                strIP = self.path[lastSlash + 1:]
                strIMG = _hostinfo.getGeoImagebyIPv6new(strIP)

                f = open(curdir + sep + strIMG, "rb") 
                self.send_response(200)

                month = timedelta(days=30)
                futuredate = date.today() + month
                self.send_header('Expires',futuredate.strftime('%a, %d %b %Y %H:%M:%S GMT'))
                self.send_header('Content-type','image/png')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()

                #self.send_response(301)
                #self.send_header("Location", strIMG)
                #self.end_headers()
                #self.output("")
            # v2 REST API - get whois for domain
            elif "whois.ncc" in self.path:
                lastSlash = self.path.rfind("/")
                strDomain = self.path[lastSlash + 1:]
                
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.output(ourwhois(strDomain))
                
            else:
               self.send_error(404,'[!] File Not Found: %s' % self.path)

        except IOError:
            self.send_error(404,'[!] File Not Found: %s' % self.path)

        except:
            pass

class MultiThreadedHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    pass

def tcpport(parameter):
    """
    Callable for converting valid TCP port number Strings into ints.

    @param parameter: The string representation of the TCP port number.
    @return: The int representation of the TCP port number if it's valid.
    @raise argparse.ArgumentTypeError: If the given value is invalid.
    """
    try:
        int_param = int(parameter)
    except ValueError:
        raise argparse.ArgumentTypeError("Port number needs to be an integer")
    if not int_param in range(1, 65536):
        raise argparse.ArgumentTypeError("Port number needs to be between 1 and 65535")
    return int_param

if __name__ == '__main__':
    
    print ("[i] NCC Group domain typofinder - https://github.com/nccgroup")

    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--port', help='Port to listen on',required=False, type=tcpport, default=801)
    parser.add_argument('-a','--address', help='hostname / IP address to bind to',required=False, type=str, default='')
    parser.add_argument('-k','--key',help='Google SafeBrowsing API key', required=False)
    args = parser.parse_args()

    if args.key:
        KEY = args.key	

    try:   
        httpd = MultiThreadedHTTPServer((args.address, args.port), MyHandler)
    except socket.gaierror:
        print("[!] Supplied address invalid! exiting!")
        sys.exit()

    print ("[i]", time.asctime(), " Server Starts - %s:%s" % (args.address, args.port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    
    httpd.server_close()
    print ("[i]", time.asctime(), " Server Stops - %s:%s" % (args.address, args.port))
