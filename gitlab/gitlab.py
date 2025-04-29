import json
import re
import requests
import urllib

class Gitlab:
  _api_url = None
  _headers = None

  def __init__(self, url, token):
    setattr(self, '_api_url', url+'/api/v4')
    setattr(self, '_headers', { 'PRIVATE-TOKEN' : token })
    r = requests.get('/'.join([self._api_url,'projects']), headers=self._headers)
    if (r.status_code != requests.codes.ok):
        raise AuthenticationError("Invalid token")

  def findGroup(self, name):
      group = GitlabGroup()
      r = requests.get('/'.join([self._api_url,'groups',urllib.parse.quote_plus(name)]), headers=self._headers)
      if r.status_code == requests.codes.ok:
          g = json.loads(r.text or r.content)
          if g['name'] == name:
              group = GitlabGroup(g['id'], g['name'], g['path'])
      return group

  def createGroup(self, name):
      # Make sure group doesn't exist
      group = self.findGroup(name)
      if group.id == -1:
          payload={ 'name': name, 'path': name}
          r = requests.post('/'.join([self._api_url,'groups']), payload, headers=self._headers)
          if r.status_code == 201:
              g = json.loads(r.text or r.content)
              group = GitlabGroup(g['id'], g['name'], g['path'])
      return group

  def findProject(self, name, group=None):
      project = GitlabProject()
      if group != None:
          grpName=""
          print(f"debug: {type(group)}")
          if isinstance(group, str):
              grpName = group
          elif isinstance(group, GitlabGroup):
              grpName = group.name
          projectUrl=urllib.parse.quote_plus('/'.join([grpName,name]))
          r = requests.get('/'.join([self._api_url,'projects',projectUrl]), headers=self._headers)
          if r.status_code == requests.codes.ok:
              p = json.loads(r.text or r.content)
              project = GitlabProject(p['id'], p['path'], p['path_with_namespace'],
                                      p['web_url'], p['wiki_enabled'])
      return project

  def createProject(self, name, group, wiki_enabled=False):
      project = GitlabProject()
      g = GitlabGroup()
      # Check if group exists, if not create group
      if isinstance(group, str):
          g = self.findGroup(group)
      elif isinstance(group, GitlabGroup):
          g = self.findGroup(group.name)
      if g.id < 0:
          if isinstance(group, str):
              g = self.createGroup(group)
          elif isinstance(group, GitlabGroup):
              g = self.createGroup(group.name)
      # TODO: see what import_url does
      payload = { 'name': name, 'namespace_id': g.id, 'wiki_enabled': str(wiki_enabled).lower() }
      r = requests.post('/'.join([self._api_url,'projects']), payload, headers=self._headers)
      if r.status_code == 201:
          p = json.loads(r.text or r.content)
          project = GitlabProject(p['id'], p['path'], p['path_with_namespace'],
                                  p['web_url'], p['wiki_enabled'])
      return project

  def mirrorRepo(self, source_url, group, GHtoken, id):

    mirror_data = {
        'enabled': True,
        'url': source_url,
        'auth_user': group,
        'auth_password': GHtoken,
        'mirror_overwrites_diverged_branches': True
    }


    #Configure pull mirroring for project
    r = requests.put(source_url, headers=self._headers, data=mirror_data)


    #Start mirror pulling
    pull = requests.post('/'.join([self._api_url, 'projects', id,'mirror','pull']), headers=self._headers)
    #needs error handling


  def touchProjectWiki(self, project):
      """Does a simple get request on the wiki url to force the
      creating of the wiki repository."""
      r = requests.get(project.wiki_url, headers=self._headers)

class GitlabGroup:
    id = -1
    name = None
    path = None

    def __init__(self, id=-1, name=None, path=None):
        setattr(self, 'id', id)
        setattr(self, 'name', name)
        setattr(self, 'path', path)

class GitlabProject:
    id = -1
    wiki_enabled = False
    name = None
    path = None
    web_url = None
    wiki_url = None
    wiki_path = None

    def __init__(self, id=-1, name=None, path=None, url=None, wiki_enabled=False):
        setattr(self, 'id', id)
        setattr(self, 'name', name)
        setattr(self, 'web_url', url)
        setattr(self, 'wiki_enabled', wiki_enabled)
        if path:
            setattr(self, 'path', path+'.git')
        if wiki_enabled:
            setattr(self, 'wiki_url', url+'/wikis/home')
            setattr(self, 'wiki_path', path+'.wiki.git')

class AuthenticationError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        print(": Unable to authenticate to gitlab API:", repr(self.value))
