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
from argformatter import smartformatter



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

            print("");

        elif args.verbose is True and args.onlyactive is False:
            print (strDEntityJSON['strDomain']+",notactive," + strDEntityJSON['strError'])
    else:
        if strDEntityJSON['bError'] is False:
            print(strDEntityJSON['strDomain'] + ",active")                           
        elif args.errors is True:
            print(strDEntityJSON['strDomain'] + ",notactive,"+strDEntityJSON['strError'])                           


def tryDomain(strURLEntity,strURLEntityDetail,dataFoo,strHTTPHdrs, intDepth):
    arrDomainResp = requests.post(strURLEntity, data=dataFoo, headers=strHTTPHdrs, verify=args.certchecks)

    if arrDomainResp.status_code != requests.codes.ok:
        print("[!] Recieved error from web service during getting basic details")
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
        parser.add_argument('-d', '--domain', help='domain to analyze', required=True, type=str)
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
        parser.set_defaults(verbose=False)
        parser.set_defaults(errors=False)
        parser.set_defaults(domainsonly=False)
        parser.set_defaults(nobanners=False)
        parser.set_defaults(certchecks=False)
        parser.set_defaults(onlyactive=False)
        parser.set_defaults(information=False)
        parser.set_defaults(pretty=False)
        args = parser.parse_args()

        if args.nobanners is False:
            print("[i] NCC Group DNS typo domain command line client - https://labs.nccgroup.trust");

        if args.verbose is False and args.information is True:
            print("[!] you can't specify information without verbose")
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

        if args.typos == 1:
            args.typos = 0
        elif args.typos == 2:
            args.typos = 50
        elif args.typos == 3:
            args.typos = 100

        if args.charset == 1:
            args.charset = 0
        elif args.charset == 2:
            args.charset = 50
        elif args.charset == 3:
            args.charset = 100


        strHTTPHdrs      = {'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Accept': 'text/plain'}
        strTypoRequest   = "host="+args.domain+"&typos=typos&typoamount=" + str(args.typos) + "&tld=tld&bitflip=bitflip&homoglyph=homoglyph&doppelganger=doppelganger&charsetamount=" + str(args.charset) + "&alexafilter=neveralexa"
        strEntityRequest = "host="
    
        if args.nobanners is False or args.pretty is True:
            print("[i] Getting typo domains list....")
        
        arrTypoResp = requests.post(strURLTypos, data=strTypoRequest, headers=strHTTPHdrs, verify=args.certchecks)

        if arrTypoResp.text.startswith("[!]"):
            print(arrTypoRest.text)
            sys.exit(0)

        strTypoJSON = arrTypoResp.json()

        if args.nobanners is False:
            print("[i] Total typo domains to check " + str(len(strTypoJSON)))

        if args.domainsonly is True:
            for strTDomain in strTypoJSON:
                print(strTDomain)
            sys.exit(0)      

        

        if args.nobanners is False:
            print("[i] Checking typo domains list for active domains....")

        strDomain = ""
        for strTDomain in strTypoJSON:
            intDepth = 0
            dataFoo = strEntityRequest+strTDomain
            try:           
                tryDomain(strURLEntity,strURLEntityDetail,dataFoo,strHTTPHdrs, intDepth)

            except UnicodeDecodeError:
                pass

            except ConnectionAbortedError:
                intDepth = intDepth + 1
                if intDepth > 4:
                    print("[!] Connection abort whilst checking " + print(strDomain))
                else:
                    tryDomain(strURLEntity,strURLEntityDetail,dataFoo,strHTTPHdrs, intDepth)
            except ConnectionError:
                intDepth = intDepth + 1
                if intDepth > 4:
                    print("[!] Connection error whilst checking " + print(strDomain))
                else:
                    tryDomain(strURLEntity,strURLEntityDetail,dataFoo,strHTTPHdrs, intDepth)

            except requests.exceptions.ConnectionError:
                intDepth = intDepth + 1
                if intDepth > 4:
                    print("[!] Connection error whilst checking " + print(strDomain))
                else:
                    tryDomain(strURLEntity,strURLEntityDetail,dataFoo,strHTTPHdrs, intDepth)

    except ConnectionAbortedError:
        print("[!] Connection abort getting list of domains")
        pass

    except ConnectionError:
        print("[!] Connection error getting list of domains")
        pass
    
    except requests.exceptions.ConnectionError:
        print("[!] Connection error getting list of domains")
        pass

    except (KeyboardInterrupt, BrokenPipeError, SystemExit):
        pass

    #except:
    #    type, value, traceback = sys.exc_info()
    #    print("[i] Other error - " + str(type) + " - " + str(value))