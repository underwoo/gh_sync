import json
import re
import requests

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
    # check if type is known
    # TODO: Need to throw an exception
    if (type!='users' and type!='orgs'):
      print("Need to throw an exception --- Just not sure what kind yet")
    url=self._api_url+type+'/'+name+'/repos'
    try:
        r = requests.get(url, headers=self._headers)
    except:
        print("An error has occured.")
        raise
    if (r.status_code != requests.codes.ok):
        raise URLNotFound(url)
    rs = json.loads(r.text or r.content)
    ghr = []
    for repo in rs:
      repo_has_wiki=repo['has_wiki'] and repo['has_pages']
      ghr.append(GithubRepo(repo['name'], repo['ssh_url'], repo['clone_url'], repo_has_wiki))
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
  ssh_url = None
  name = None
  has_wiki = False
  wiki_url = None
  wiki_ssh_url = None

  def __init__(self, name, ssh_url, clone_url, has_wiki):
    setattr(self, 'name', name)
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
        print(": ")

class URLNotFound(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        print(": Unable to find URL:", self.value)

class AuthenticationError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        print(": Unable to authenticate to github API:", repr(self.value))
