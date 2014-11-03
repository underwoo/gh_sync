import json
import re
import requests

class Gitlab:
  _api_url = None
  _headers = None

  def __init__(self, url, token):
    setattr(self, '_api_url', url+'/api/v3/')
    setattr(self, '_headers', { 'PRIVATE-TOKEN' : token })
    r = requests.get(self._api_url, headers=self._headers)
    if (r.status_code != requests.codes.ok):
        raise AuthenticationError("Invalid token")

  def findGroup(self, name):
      group = GitlabGroup()
      r = requests.get(self._api_url+'groups', headers=self._headers)
      if r.status_code == requests.codes.ok:
          groups = json.loads(r.text or r.content)
          for g in groups:
              if g['name'] == name:
                  group = GitlabGroup(g['id'], g['name'], g['path'], g['owner_id'])
                  break
      return group

  def createGroup(self, name):
      # Make sure group doesn't exist
      group = self.findGroup(name)
      if group.id == -1:
          payload={ 'name': name, 'path': name}
          r = requests.post(self._api_url+'groups', payload, headers=self._headers)
          if r.status_code == 201:
              g = json.loads(r.text or r.content)
              group = GitlabGroup(g['id'], g['name'], g['path'], g['owner_id'])
      return group

  def findProject(self, name, group=None):
      project = GitlabProject()
      urlName = ''
      if group != None:
          # Append group name to project name
          if isinstance(group, unicode) or isinstance(group, str):
              urlName = self._urlEncodeProjectName(self._translateRepoName(group+'/'+name))
          elif isinstance(group, GitlabGroup):
              urlName = self._urlEncodeProjectName(self._translateRepoName(group.name+'/'+name))
      else:
          urlName = self._urlEncodeProjectName(name)
      r = requests.get(self._api_url+'projects/'+urlName, headers=self._headers)
      if r.status_code == requests.codes.ok:
          p = json.loads(r.text or r.content)
          project = GitlabProject(p['id'], p['path'], p['path_with_namespace'],
                                  p['web_url'], p['wiki_enabled'])
      return project

  def createProject(self, name, group, wiki_enabled=False):
      project = GitlabProject()
      g = GitlabGroup()
      # Check if group exists, if not create group
      if isinstance(group, str) or isinstance(group, unicode):
          g = self.findGroup(group)
      elif isinstance(group, GitlabGroup):
          g = self.findGroup(group.name)
      if g.id < 0:
          if isinstance(group, str) or isinstance(group, unicode):
              g = self.createGroup(group)
          elif isinstance(group, GitlabGroup):
              g = self.createGroup(group.name)
      # TODO: see what import_url does
      payload = { 'name': name, 'namespace_id': g.id, 'wiki_enabled': str(wiki_enabled).lower() }
      r = requests.post(self._api_url+'projects', payload, headers=self._headers)
      if r.status_code == 201:
          p = json.loads(r.text or r.content)
          project = GitlabProject(p['id'], p['path'], p['path_with_namespace'],
                                  p['web_url'], p['wiki_enabled'])
      return project

  def touchProjectWiki(self, project):
      """Does a simple get request on the wiki url to force the
      creating of the wiki repository."""
      r = requests.get(project.wiki_url, headers=self._headers)

  def _translateRepoName(self, repo):
      # Need to downcase string as well
      return re.sub('\.', '-', repo.lower())

  def _urlEncodeProjectName(self, string):
      stringFixed = re.sub('/', '%2F', string.lower())
      stringFixed = re.sub('\.', '%2E', stringFixed)
      stringFixed = re.sub(' ', '%20', stringFixed)
      return stringFixed

class GitlabGroup:
    id = -1
    name = None
    path = None
    owner_id = -1

    def __init__(self, id=-1, name=None, path=None, owner_id=-1):
        setattr(self, 'id', id)
        setattr(self, 'name', name)
        setattr(self, 'path', path)
        setattr(self, 'owner_id', owner_id)

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
        print ": Unable to authenticate to gitlab API:", repr(self.value)
