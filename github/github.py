import json
import re
import requests
import sys
from urllib.parse import urljoin

class Github:
    _api_url = 'https://api.github.com/'
    _headers = None

    def __init__(self, token=None):
        setattr(self, '_headers', {'Authorization': "token "+token})
        # Check if token is valid
        r = requests.get(self._api_url, headers=self._headers)
        if (r.status_code != requests.codes.ok):
            raise AuthenticationError("Invalid token")

    def getRepos(self, name, type):
        # Return an empty list if nothing found
        ghr = []
        # check if type is known
        if (type!='users' and type!='orgs'):
            raise OwnerTypeError(type)
        url=urljoin(self._api_url, "/".join([type, name, "repos"]))
        # Indicate if there are more pages of data from GitHub
        more_pages = True
        while more_pages:
            try:
                r = requests.get(url, headers=self._headers)
            except:
                print("Error getting GitHub {type} repositories for {name}",
                      file=sys.stderr)
                raise
            if (r.status_code != requests.codes.ok):
                raise URLNotFound(url)

            rs = json.loads(r.text or r.content)

            for repo in rs:
                repo_has_wiki=repo['has_wiki'] and repo['has_pages']
                ghr.append(GithubRepo(repo['id'],
                                      repo['name'],
                                      repo['full_name'],
                                      repo['ssh_url'],
                                      repo['clone_url'],
                                      repo_has_wiki))

            # Check if there are more pages
            if "next" in r.links:
                url = r.links["next"]["url"]
            else:
                more_pages = False

        return ghr

    def createWebHook(self, group, repo, gl_api):

        webhook_data = {
            'name': 'web',
            'active': True,
            'events': ['push'],
            'config': ({
                'url': gl_api,
                'content_type': 'json',
                'insecure_ssl': '0'
            })
        }
        #may require additional headers
        r = requests.post('/'.join([self._api_url, 'repos', group, repo, 'hooks']), headers=self._headers, data=webhook_data)
        #needs error handling


class GithubRepo:
    id = -1
    ssh_url = None
    name = None
    has_wiki = False
    wiki_url = None
    wiki_ssh_url = None

    def __init__(self, id, name, full_name, ssh_url, clone_url, has_wiki):
        setattr(self, 'id', id)
        setattr(self, 'name', name)
        setattr(self, 'full_name', full_name)
        setattr(self, 'ssh_url', ssh_url)
        setattr(self, 'clone_url', clone_url)
        setattr(self, 'has_wiki', has_wiki)
        if (has_wiki):
            setattr(self, 'wiki_url', re.sub(r"\.git$", ".wiki.git", self.clone_url))
            setattr(self, 'wiki_ssh_url', re.sub(r"\.git$", ".wiki.git", self.ssh_url))


class ConnectionError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return f": {repr(self.value)}"


class URLNotFound(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return f": Unable to find URL: {repr(self.value)}"


class AuthenticationError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return f": Unable to authenticate to github API: {repr(self.value)}"


class OwnerTypeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return f": Unknown GitHub owner type: {repr(self.value)}"
