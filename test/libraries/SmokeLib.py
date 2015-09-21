import requests
__author__ = 'shawkins'
"""
Yes, this filename does not comply with PEP8. Thank robotframework for that.
"""


class SmokeLib(object):
    def get_url_http_status(self, url):
        r = requests.get(url)
        return r.status_code
