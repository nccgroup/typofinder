#
# Typofinder for domain typo discovery
# 
# Released as open source by NCC Group Plc - http://www.nccgroup.com/
# 
# Developed by Ollie Whitehouse, ollie dot whitehouse at nccgroup dot com
#
# http://www.github.com/nccgroup/typofinder
#
# Released under AGPL see LICENSE for more information
#

import sys
import codecs
import argparse
import requests
import simplejson
import urllib.request
from argformatter import smartformatter
from bs4 import BeautifulSoup


def getWebTitle(strDomain):
    
    arrProtos = ['https','http']
    arrSites = ['www','m']
    
    strRes=""
    arrTmp = []
    for strProto in arrProtos:
        for strSite in arrSites:

            try:
                #print(strProto+"://" + strSite + "." + strDomain)
                soup = BeautifulSoup(urllib.request.urlopen(strProto+"://" + strSite + "." + strDomain + "/"), "html5lib")
                #print(strProto + " - " + strSite + " - " + soup.title.string)
                arrTmp.append(",")
                arrTmp.append(strProto)
                arrTmp.append(":")
                arrTmp.append(strSite)
                arrTmp.append(":")
                if soup and soup.title and soup.title.string:
                    arrTmp.append(soup.title.string.replace(",",""))
                else:
                    arrTmp.append("nontitle")
            except:
                type, value, traceback = sys.exc_info()
                #print("[i] Get title error - " + str(type) + " - " + str(value))
                pass

    strRes = ''.join(arrTmp).replace("\n","")
    return strRes

def printPretty(strDEntityJSON,strDEntityInfoJSON):
    if args.verbose is True:
        if strDEntityJSON['bError'] is False:
            print("[i] Domain  +- " + strDEntityJSON['strDomain'])
            print("[i]         |")
            print("[i]         +----- Active")

            for server in strDEntityJSON['nameservers']:
                print("[i]         |")
                print("[i]         +----- DNS server - " + server);
                print("[i]")
            
            if args.information is True:
                for server in strDEntityInfoJSON['aMX']:
                    print("[i]         |")
                    print("[i]         +----- MX server - " + server);
                    print("[i]")

                for server in strDEntityInfoJSON['IPv4Addresses']:
                    print("[i]         |")
                    print("[i]         +----- IPv4 Address (A) - " + server);
                    print("[i]")

                for server in strDEntityInfoJSON['IPv6Addresses']:
                    print("[i]         |")
                    print("[i]         +----- IPv6 Address (AAAA) - " + server);
                    print("[i]")

        elif args.verbose is True and args.onlyactive is False:
            print("[i] Domain   +- " + strDEntityJSON['strDomain'])
            print("[i]          |")
            print("[i]          +----- Not Active - " + strDEntityJSON['strError'])
            print("[i]")
    else:
        if strDEntityJSON['bError'] is False:
            print("[i] Domain  +- " + strDEntityJSON['strDomain'])
            print("[i]         |")
            print("[i]         +----- Active")                           
            print("[i]")

        elif args.errors is True:
            print("[i] Domain  +- " + strDEntityJSON['strDomain'])
            print("[i]         |")
            print("[i]         +----- Not Active - " + strDEntityJSON['strError'])
            print("[i]")

def printNotPretty(strDEntityJSON,strDEntityInfoJSON):
    if args.verbose is True:
        if strDEntityJSON['bError'] is False:
            print(strDEntityJSON['strDomain']+",active",end="")
            for server in strDEntityJSON['nameservers']:
                print (",NS:" + server,end="");

                if args.information is True:
                    for server in strDEntityInfoJSON['aMX']:
                        print (",MX:" + server,end="");

                    for server in strDEntityInfoJSON['IPv4Addresses']:
                        print (",A:" + server,end="");

                    for server in strDEntityInfoJSON['IPv6Addresses']:
                        print (",AAAA:" + server,end="");

                if args.gettitle is True:
                    try:
                        print(getWebTitle(strDEntityJSON['strDomain']),end="")
                    except:
                        pass

            print("");

        elif args.verbose is True and args.onlyactive is False:
            print (strDEntityJSON['strDomain']+",notactive," + strDEntityJSON['strError'])
    else:
        if strDEntityJSON['bError'] is False:
            print(strDEntityJSON['strDomain'] + ",active",end="")
            if args.gettitle is True:
                try:
                    print(getWebTitle(strDEntityJSON['strDomain']),end="")
                except:
                    pass
            print("");
        elif args.errors is True:
            print(strDEntityJSON['strDomain'] + ",notactive,"+strDEntityJSON['strError'])                           


def tryDomain(strURLEntity,strURLEntityDetail,dataFoo,strHTTPHdrs, intDepth):
    arrDomainResp = requests.post(strURLEntity, data=dataFoo, headers=strHTTPHdrs, verify=args.certchecks)

    if arrDomainResp.status_code != requests.codes.ok:
        print("[!] Recieved error from web service during getting basic details - " + str(arrDomainResp.status_code)) 
        return
       
    try:
        strDEntityJSON = arrDomainResp.json()

        if strDEntityJSON['bError'] is False and args.information is True:
            arrDomainRespInfo = requests.post(strURLEntityDetail, data=dataFoo, headers=strHTTPHdrs, verify=args.certchecks)

            if arrDomainRespInfo.status_code != requests.codes.ok:
                print("[!] Recieved error from web service getting full details")
                return
            else:
                strDEntityInfoJSON = arrDomainRespInfo.json()
        else:
            strDEntityInfoJSON = None

        if args.pretty is False:
            printNotPretty(strDEntityJSON,strDEntityInfoJSON)
        else:
            printPretty(strDEntityJSON,strDEntityInfoJSON)

    except simplejson.scanner.JSONDecodeError:
        print("[!] JSON decode error")

if __name__ == '__main__':


    try:
        parser = argparse.ArgumentParser(formatter_class=smartformatter)
        
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-d', '--domain', help='domain to analyze', type=str)
        group.add_argument('-b', '--bulkfile',   help='bulk import domains to analyze from this file', required=False, type=str)

        parser.add_argument('-s', '--server',   help='server to use', required=False, type=str, default='https://labs.nccgroup.trust')
        parser.add_argument('-v', '--verbose',   help='verbose output', required=False, dest='verbose', action='store_true')
        parser.add_argument('-o', '--onlyactive',   help='only active domain verbose output', required=False, dest='onlyactive', action='store_true')
        parser.add_argument('-e', '--errors',   help='show errors in non verbose mode', required=False, dest='errors', action='store_true')
        parser.add_argument('-l', '--listdomains',   help='list the domains and exit', required=False, dest='domainsonly', action='store_true')
        parser.add_argument('-n', '--nobanners',   help='display only data', required=False, dest='nobanners', action='store_true')
        parser.add_argument('-m', '--makesecure',   help='enable SSL/TLS verification', required=False, dest='enablesecurity', action='store_true')
        parser.add_argument('-i', '--information',   help='detailed DNS records for the domain', required=False, dest='information', action='store_true')
        parser.add_argument('-c', '--charset',   help="R|char set complexity on a scale of 1 to 3\n"
                                                      "1 = ASCII\n" 
                                                      "2 = RFC3491\n"
                                                      "3 = All (default)\n"
                                                      , type=int, required=False, dest='charset', choices=[1,2,3], default=3)
        parser.add_argument('-t', '--typos',   help="R|degree to which to generate typos on a scale of 1 to 3\n"
                                                     "1 = quick\n"
                                                     "2 = balanced\n"
                                                     "3 = rigorous (default)\n", type=int, required=False, dest='typos', choices=[1,2,3], default=3)
        parser.add_argument('-p', '--pretty',   help='pretty output', required=False, dest='pretty', action='store_true')
        parser.add_argument('-g', '--gettitle', help='get webpage title if possible', required=False, dest='gettitle', action='store_true')
        parser.add_argument('-w', '--write', help='write list of domains to file', required=False, dest='write', action='store_true')
        parser.set_defaults(verbose=False)
        parser.set_defaults(errors=False)
        parser.set_defaults(domainsonly=False)
        parser.set_defaults(nobanners=False)
        parser.set_defaults(certchecks=False)
        parser.set_defaults(onlyactive=False)
        parser.set_defaults(information=False)
        parser.set_defaults(pretty=False)
        parser.set_defaults(gettitle=False)
        parser.set_defaults(write=False)
        args = parser.parse_args()

        if args.nobanners is False:
            print("[i] NCC Group DNS typo domain command line client - https://labs.nccgroup.trust");

        if args.verbose is False and args.information is True:
            print("[!] you can't specify information without verbose")
            sys.exit(-1)

        if args.pretty is True and args.gettitle is True:
            print("[!] you can't get web page titles with pretty printing")
            sys.exit(-1)

            
        # this is filth
        if sys.platform == 'win32':
            try:
                import win_unicode_console
                win_unicode_console.enable()
            except:
                print("[!] NOTE: on Microsoft Windows this needs win-unicode-console installed");
                sys.exit(-1)

        requests.packages.urllib3.disable_warnings()
    
        strURLTypos  = args.server + "/typofinder/typov2.ncc"
        strURLEntity = args.server +  "/typofinder/entitylight.ncc"
        strURLEntityDetail = args.server +  "/typofinder/entity.ncc"

        # do not change these unless server side is updated
        if args.typos == 1:
            args.typos = 0
        elif args.typos == 2:
            args.typos = 1
        elif args.typos == 3:
            args.typos = 100

        # do not change these unless server side is updated
        if args.charset == 1:
            args.charset = 0
        elif args.charset == 2:
            args.charset = 50
        elif args.charset == 3:
            args.charset = 100

        lstSrcDomains = list()
        
        # bulk or not
        if args.bulkfile and len(args.bulkfile) > 0:
            if args.nobanners is False or args.pretty is True:
                print("[i] Doing bulk analysis..")
                
            try:
                for line in open(args.bulkfile):
                    if args.nobanners is False or args.pretty is True:
                        print("[i] Adding " + line.rstrip('\n') + " for analysis")
                    lstSrcDomains.append(line.rstrip('\n'))
            except:                               
                type, value, traceback = sys.exc_info()
                print("[!] Error processing bulk import " + args.bulkfile + " - " + str(type) + " - " + str(value))
                sys.exit(-1)


        else:
            if args.nobanners is False or args.pretty is True:
                print("[i] Doing single domain analysis..")                           
            lstSrcDomains.append(args.domain)
        
           
        
        for doitDomain in lstSrcDomains:
            strHTTPHdrs      = {'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Accept': 'text/plain'}
            strTypoRequest   = "host="+doitDomain+"&typos=typos&typoamount=" + str(args.typos) + "&tld=tld&bitflip=bitflip&homoglyph=homoglyph&doppelganger=doppelganger&charsetamount=" + str(args.charset) + "&alexafilter=neveralexa"
            strEntityRequest = "host="
    
            if args.nobanners is False or args.pretty is True:
                print("[i] Getting typo domains list for " + doitDomain + "....")
        
            arrTypoResp = requests.post(strURLTypos, data=strTypoRequest, headers=strHTTPHdrs, verify=args.certchecks)

            if arrTypoResp.text.startswith("[!]"):
                print(arrTypoResp.text)
                sys.exit(0)

            strTypoJSON = arrTypoResp.json()

            if args.nobanners is False:
                print("[i] Total typo domains to check for " + doitDomain + " are " + str(len(strTypoJSON)))

            if args.domainsonly is True:
                if args.write is True:
                    target = open(doitDomain+".txt", 'wb')
                    
                for strTDomain in strTypoJSON:
                    if args.write is True:
                        strOut = str(strTDomain).encode('utf8')
                        target.write(strOut)
                        target.write(bytes("\n",'UTF-8'))
                    else:
                        print(strTDomain)
                sys.exit(0)      

        

            if args.nobanners is False:
                print("[i] Checking typo domains list for " + doitDomain + " for active domains....")

            strDomain = ""
            for strTDomain in strTypoJSON:
                intDepth = 0
                dataFoo = strEntityRequest+strTDomain
                try:           
                    tryDomain(strURLEntity,strURLEntityDetail,dataFoo,strHTTPHdrs, intDepth)

                except UnicodeDecodeError:
                    pass

                except UnicodeEncodeError:
                    pass

                #except ConnectionAbortedError:
                #    intDepth = intDepth + 1
                #    if intDepth > 4:
                #        print("[!] Connection abort whilst checking " + print(strDomain))
                #    else:
                #        tryDomain(strURLEntity,strURLEntityDetail,dataFoo,strHTTPHdrs, intDepth)
                
                #except ConnectionError:
                #    intDepth = intDepth + 1
                #    if intDepth > 4:
                #        print("[!] Connection error whilst checking " + print(strDomain))
                #    else:
                #        tryDomain(strURLEntity,strURLEntityDetail,dataFoo,strHTTPHdrs, intDepth)

                except requests.exceptions.ConnectionError:
                    pass
                #    intDepth = intDepth + 1
                #    if intDepth > 4:
                #        print("[!] Connection error whilst checking " + print(strDomain))
                #    else:
                #        tryDomain(strURLEntity,strURLEntityDetail,dataFoo,strHTTPHdrs, intDepth)

                except ConnectionError:
                    pass

                except:
                    type, value, traceback = sys.exc_info() 
                    print("[i] Other error - " + str(type) + " - " + str(value))

    except ConnectionAbortedError:
        pass

    except ConnectionError:
        pass

    except requests.exceptions.ConnectionError:
        pass

    except (KeyboardInterrupt, BrokenPipeError, SystemExit):
        sys.exit(0)

    except:
        type, value, traceback = sys.exc_info()
        print("[i] Other error - " + str(type) + " - " + str(value))