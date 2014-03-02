import re
from dns.exception import DNSException
import dns.resolver
from dns.resolver import NXDOMAIN
from extrainfoquery import ExtraInfoQuery


class Spamhaus(ExtraInfoQuery):
    """Spamhaus Integration class"""

    _url_regex = re.compile(r'^.*"(http:.*)"$')

    def __init__(self):
        self._resolver = dns.resolver.Resolver()
        self._resolver.Timeout = 2.0
        self._resolver.lifetime = 2.0
        self._resolver.cache = dns.resolver.LRUCache()

        #Use OpenDNS name servers, as not all name servers will respond to spamhaus queries, e.g. Google.
        self._resolver.nameservers = ['208.67.222.222', '208.67.220.220']

    def query(self, hostname, ipaddress):
        """
        Example blocked IP: 127.0.0.2

        @param hostname: Ignored
        """
        ipparts = ipaddress.split('.')
        ipparts.reverse()
        reverseipaddress = '.'.join(ipparts)
        queryname = reverseipaddress + ".zen.spamhaus.org"

        try:
            self._resolver.query(queryname, "A")
            short_msg = "Spamhaus Blocked"
        except NXDOMAIN:
            return None, None
        except DNSException:
            return "DNS Failure", ""

        detail_msg = ""
        txt_result_answer = self._resolver.query(queryname, "TXT")
        for txt_result_line in txt_result_answer.rrset:
            match = self._url_regex.match(str(txt_result_line))
            if match:
                detail_msg += "See: <a href=\"" + match.group(1) + "\">" + match.group(1) + "</a> "

        return short_msg, detail_msg
