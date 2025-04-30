import json
import requests
import urllib
import urllib.parse
import sys

import github

class Gitlab:
    _api_url = None
    _headers = None

    def __init__(self, url, token):
        """Initailze a connection to a GitLab instance using the v4 API.

        Arguments

        url: Base URL to the GitLab instance
        token: A GitLab access token.  The token must have at least the
            API and write_repository scopes.
        """
        setattr(self, '_api_url', urllib.parse.urljoin(url, "api/v4"))
        setattr(self, '_headers', { 'PRIVATE-TOKEN' : token })
        try:
            r = requests.get('/'.join([self._api_url,
                                       'projects']),
                             headers=self._headers)
        except Exception:
            print(f"Error connecting to \"{self._api_url}\"",
                  file=sys.stderr)
            raise
        if (r.status_code != requests.codes.ok):
            if r.status_code == 401:
                raise AuthenticationError("Invalid token")
            else:
                raise ConnectionError(r.status.code, r.reason)

    def findGroup(self, name):
        """Find a GitLab group.

        Arguments

        name: Name of the GitLab group to find.
        """
        group = None
        r = requests.get('/'.join([self._api_url,
                                   'groups',
                                   urllib.parse.quote_plus(name)]),
                         headers=self._headers)
        if r.status_code == requests.codes.ok:
            g = json.loads(r.text or r.content)
            if g['name'] == name:
                group = GitlabGroup(g['id'], g['name'], g['path'])
        return group

    def createGroup(self, name):
        """Create a GitLab group

        Arguments

        name: Name of the GitLab group
        """
        # Make sure group doesn't exist
        group = self.findGroup(name)
        if group.id == -1:
            payload={ 'name': name, 'path': name}
            r = requests.post('/'.join([self._api_url,
                                        'groups']),
                              payload,
                              headers=self._headers)
            if r.status_code == 201:
                g = json.loads(r.text or r.content)
                group = GitlabGroup(g['id'], g['name'], g['path'])
        return group

    def findProject(self, name, group=None):
        """Find a GitLab project, and return a GitlabProject object.

        Arguments:

        name: GitLab project name to find.
        group: GitLab group that should contain the project.
        """
        # An Empty project as a default return
        project = GitlabProject
        if group != None:
            grpName=""
            if isinstance(group, str):
                grpName = group
            elif isinstance(group, GitlabGroup):
                grpName = group.name
            projectUrl = urllib.parse.quote_plus('/'.join([grpName, name]))
            r = requests.get('/'.join([self._api_url,
                                       'projects',
                                       projectUrl]),
                                       headers=self._headers,
                                       allow_redirects=False)
            if r.status_code == requests.codes.ok:
                p = json.loads(r.text or r.content)
                project = GitlabProject(p['id'],
                                        p['path'],
                                        p['path_with_namespace'],
                                        p['web_url'],
                                        p['wiki_enabled'])
        return project

    def createProject(self, name, group, wiki_enabled=False):
        """Create a GitLab project within the GitLab group.

        Arguments:

        name: GitLab project name to create
        group: GitLab group to use to create the project.  The group
               will be created if it doesn't exist.
        wiki_enabled: Indicate if the wiki should be enabled for this
               project.
        """
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

    def importGitHub(self, gh, gh_repo, gl_group):
        """Import a GitHub public repository to a GitLab namespace.
        The repository name will be the same as the GitHub repository
        name.

        Arguments:

        gh: An authenticated Github instance
        gh_repo: The GitHub.com repository to clone using the format
                "OWNER/REPO" or a GithubProject object.

        gl_group: The GitLab group where to place the imported GitHub
                  repository.
        """
        # Check that we can get the Github repository from the passed in instance
        if not isinstance(gh, github.Github):
            raise TypeError(f"The GitHub instances is an unsupported type \"{type(gh)}\"")
        gh_repo_full_name = ""
        gh_repo_name = ""
        if isinstance(gh_repo, str):
            gh_repo_full_name = gh_repo
            gh_repo_name = gh_repo.split("/")[0]
        elif isinstance(gh_repo, github.github.GithubRepo):
            gh_repo_full_name = gh_repo.full_name
            gh_repo_name = gh_repo.name
        else:
            raise TypeError(f"The Github repository is an unsupported type \"{type(gh_repo)}\"")

        # Check if the GitLab project already exists, instead of just doing the PUSH
        # If it exists, just return the project object
        gl_project = self.findProject(gh_repo_name, gl_group)
        if gl_project.id == -1:
            # The GitLab project doesn't exist, start the import
            gl_payload = {
                "personal_access_token": gh._headers['Authorization'].split()[1],
                "repo_id": gh_repo.id,
                "target_namespace": gl_group,
            }
            r = requests.post('/'.join([self._api_url, 'import', 'github']), gl_payload, headers=self._headers)
            if r.status_code == 201:
                # Project created
                gl_project = self.findProject(gh_repo_name, gl_group)
        return gl_project

    def importStatus(self, proj):
        """Get the import status of a specified GitLab project.

        Arguments:
        proj: The GitLab project, either as a GitlabProject object,
              or as a string in the format of "GROUP/PROJECT".
        """
        # Determine what type was passed
        proj_id = ""
        if isinstance(proj, str):
            try:
                [gl_group, gl_proj] = proj.split("/")
                project = self.findProject(gl_proj, gl_group)
                proj_id = str(project.id)
            except:
                print(f"Error finding GitLab project \"proj\"",
                      file=sys.stderr)
                raise
        elif isinstance(proj, GitlabProject):
            proj_id = str(proj.id)
        r = requests.get('/'.join([self._api_url,
                                   'projects',
                                   proj_id,
                                   "import"]),
                        headers=self._headers)
        status = None
        if r.status_code == requests.codes.ok:
            p = json.loads(r.text or r.content)
            status = p['import_status']
        else:
            print(f"Error getting import status: {r.status_code} {r.reason}",
                  file=sys.stderr)
        return status

    def setPullMirror(self, gl_proj, gh_repo):
        """Configure the GitLab project to pull from the GitHub
        repository.

        Arguments:

        gl_proj: The GitLab project that will pull from GitHub.  This
                 can be a type(GitlabProject), a string GROUP/PROJ, or
                 an integer with the GitLab ID.
        gh_repo: The full URL to a GitHub repository to pull from.
        """
        gl_proj_id = ""
        gl_proj_name = ""
        if isinstance(gl_proj, str):
            try:
                [gl_group, gl_proj] = gl_proj.spli("/")
                project = self.findProject(gl_proj, gl_group)
                gl_proj_id = str(project.id)
                gl_proj_name = project.name
            except:
                print(f"Error finding GitLab project \"proj\"",
                      file=sys.stderr)
                raise
        elif isinstance(gl_proj, GitlabProject):
            gl_proj_id = str(gl_proj.id)
            gl_proj_name = gl_proj.name
        # Set the github_mirror_url, and make sure it ends with ".git"
        github_mirror_url = gh_repo
        if not gh_repo.endswith(".git"):
            github_mirror_url = gh_repo + ".git"
        # Check if the GitLab repository already has mirroring setup
        # for this URL
        # Code of 200 means the repository is mirrored
        # Code of 400 means the repository is not mirrored
        r = requests.get("/".join([self._api_url,
                                   "projects",
                                   gl_proj_id,
                                   "mirror/pull"]),
                         headers=self._headers)
        if r.status_code == 200:
            # Check the URL
            p = json.loads(r.text or r.content)
            if p["url"] == github_mirror_url:
                # We do need to push a new configuration
                return True
        elif r.status_code != 400:
            # Other status codes put us in a strange state.
            raise(Exception(f"Unable to get status of pull mirror for {gl_proj_name} ({r.status_code}): {r.reason}"))

        # If we are here, update the pull configuration
        payload = {"enabled": "true",
                    "url": github_mirror_url}
        r = requests.put("/".join([self._api_url,
                                    "projects",
                                    gl_proj_id,
                                    "mirror/pull"]),
                            payload,
                            headers=self._headers)
        return True


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
        return f": Unable to authenticate to gitlab API: {repr(self.value)}"


class ConnectionError(Exception):
    def __init__(self, value, msg):
        self.value = value
        self.msg = msg
    def __str__(self):
        return f": Unable to connect to the GitLab API: {repr(self.value)} {self.msg}"
