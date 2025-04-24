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

  def touchProjectWiki(self, project):
      """Does a simple get request on the wiki url to force the
      creating of the wiki repository."""
      r = requests.get(project.wiki_url, headers=self._headers)

  def importGitHub(self, gh_repo, gl_group):
      """Import a GitHub public repository to a GitLab namespace.
      The repository name will be the same as the GitHub repository
      name.

      Arguments:

      gh_repo: The GitHub.com repository to clone using the format
               "OWNER/REPO".

      gl_group: The GitLab group where to place the imported GitHub
                repository.
      """
      # Get the GitHub repository.  Simply use requests to the GitHub.com API.
      # TODO: Update the GitHub class to get the ID
      r_gh_repo = requests.get('/'.join(["https://api.github.com", "repos", gh_repo]))
      if (r_gh_repo.status_code != requests.codes.ok):
          raise Exception(f"Unable to get GitHub repository: {gh_repo}")
      p_gh_repo = json.loads(r_gh_repo.text or r_gh_repo.content)
      # Check if the GitLab project already exists, instead of just doing the PUSH
      # If it exists, just return the project object
      gl_project = self.findProject(p_gh_repo["name"], gl_group)
      if gl_project == -1:
          # The GitLab project doesn't exist, start the import
          gl_payload = {
              "personal_access_token": "NOPE",
              "repo_id": p_gh_repo['id'],
              "target_namespace": gl_group,
          }
          r = requests.post('/'.join([self._api_url, 'import', 'github']), gl_payload, headers=self._headers)
          if r.status_code == requests.codes.ok:
              gl_project = self.findProject(p_gh_repo['name'], gl_group)
      return gl_project

  def importStatus(self, proj):
      """Get the import status of a specified GitLab project.

      Arguments:
      proj: The GitLab project, either as a GitlabProject object,
            or as a string in the format of "GROUP/PROJECT".
      """
      # Determine what type was passed
      proj_path = ""
      if isinstance(proj, str):
          proj_path = proj
      elif isinstance(proj, GitlabProject):
          proj_path = proj.path
      [gl_group, gl_proj] = proj_path.split("/")
      project = self.findProject(gl_proj, gl_group)
      r = requests.get('/'.join([self._api_url, 'projects', str(project.id), "import"]),
                       headers=self._headers)
      status = None
      if r.status_code == requests.codes.ok:
          p = json.loads(r.text or r.content)
          status = p['import_status']
      return status


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
            setattr(self, 'path', path)
        if wiki_enabled:
            setattr(self, 'wiki_url', url+'/wikis/home')
            setattr(self, 'wiki_path', path+'.wiki.git')


class AuthenticationError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        print(": Unable to authenticate to gitlab API:", repr(self.value))
