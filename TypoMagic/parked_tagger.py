import ipaddress

PARKED_IP_LIST = [ipaddress.ip_network('5.22.149.135/32'),
                  ipaddress.ip_network('8.5.1.48/28'),
                  ipaddress.ip_network('50.63.202.0/26'),
                  ipaddress.ip_network('64.74.223.32/32'),
                  ipaddress.ip_network('66.96.163.131/32'),
                  ipaddress.ip_network('68.65.123.151/32'),
                  ipaddress.ip_network('75.126.102.227/32'),
                  ipaddress.ip_network('80.92.65.144/32'),
                  ipaddress.ip_network('81.21.76.62/32'),
                  ipaddress.ip_network('83.64.127.75/32'),
                  ipaddress.ip_network('83.170.69.83/32'),
                  ipaddress.ip_network('85.25.199.30/32'),
                  ipaddress.ip_network('96.126.106.126/32'),
                  ipaddress.ip_network('109.106.161.62/32'),
                  ipaddress.ip_network('109.123.198.149/32'),
                  ipaddress.ip_network('141.8.225.237/32'),
                  ipaddress.ip_network('184.168.221.0/25'),
                  ipaddress.ip_network('185.53.177.20/32'),
                  ipaddress.ip_network('208.91.197.27/32'),
                  ipaddress.ip_network('209.222.14.3/32'),
                  ipaddress.ip_network('209.15.13.134/32'),
                 ]

PARKED_NS_LIST = ['.above.com', '.sedoparking.com',
                    '.namebrightns.com', '.namebrightdns.com', '.bodis.com',
                    '.fabulous.com', '.parking-page.net',
                    '.cashparking.com', '.dsredirection.com',
                    '.parkingcrew.net', 'buy.internettraffic.com', 'sell.internettraffic.com',
                    '.voodoo.com', '.ztomy.com', 'this-domain-for-sale.com',
                    '.dnsaddress.com', '.topdns.com',
                    '.hastydns.com', '.topdns.me', '.fastpark.net',
                    '.catadns.com', '.parkpage.foundationapi.com', '.domain-is-4-sale-at-domainmarket.com',
                    '.name-services.com',
                    '.brainydns.com', '.dnsnuts.com',
                    '.dnsauthority.com',
                    '.parked.com', '.parklogic.com', '.domainapps.com', '.klczy.com', '.yoho.com'
                  ]

def check_for_parked(typo):
    for ip in typo.IPv4Address:
        for park_range in PARKED_IP_LIST:
            ipaddr = ipaddress.ip_address(ip)
            if ipaddr in park_range:
                typo.tags.append("(parked)")
                return

    for ns in typo.nameservers:
        for parked_ns_domain in PARKED_NS_LIST:
            if ns.endswith(parked_ns_domain):
                typo.tags.append("(parked)")
                return
