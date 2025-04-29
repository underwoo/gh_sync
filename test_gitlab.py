import tomllib
import pathlib
import os
import sys

import gitlab

configFile = os.path.join(pathlib.Path.home(), ".ghsyncrc")

with open(configFile, "rb") as f:
    config = tomllib.load(f)

gl_token = config["gitlab-token"]
gl_url = config["gitlab-url"]
gl = gitlab.Gitlab(gl_url, gl_token)

test_project = "test/FMS"
print(f"Import Status (by name): {gl.importStatus(test_project)}")
project = gl.findProject("FMS", "test")
print(f"Import Status (by project): {gl.importStatus(project)}")

test_group = "gitlabUtilities"

print(f"Find group \"{test_group}\" by name.  Print some information about the group")
group = gl.findGroup(test_group)
print(f"Group ID: {group.id}")
print(f"Group Name: {group.name}")
print(f"Group Path: {group.path}")

test_project = "gh_sync"
print(f"Find project \"{test_project}\" in group \"{test_group}\", both by name.",
      "Print information about the project")
project = gl.findProject(test_project, test_group)
print(f"Project ID: {project.id}")
print(f"Project Wiki: {project.wiki_enabled}")
print(f"Project Name: {project.name}")
print(f"Project Path: {project.path}")
print(f"Project Web URL: {project.web_url}")
print(f"Project Wiki URL: {project.wiki_url}")
print(f"Project Wiki Path: {project.wiki_path}")

print(f"Find project \"{test_project}\" in group \"{test_group}\", project by name, group by object",
      "Print information about the project")
project = gl.findProject('gh_sync', group)
print(f"Project ID: {project.id}")
print(f"Project Wiki: {project.wiki_enabled}")
print(f"Project Name: {project.name}")
print(f"Project Path: {project.path}")
print(f"Project Web URL: {project.web_url}")
print(f"Project Wiki URL: {project.wiki_url}")
print(f"Project Wiki Path: {project.wiki_path}")

print("Look for an group that doesn't exist",
      "The group ID should be \"-1\"")
group = gl.findGroup('noGroup')
print(f"Group ID: {group.id}")

# Everything below was tested, but as I was testing against a
# production server, I have left this as commented out, for now.

# test_project = "test_project"
# test_group = "test"
# print(f"Create \"{test_project}\" in group \"{test_group}\".",
#       "Print information about the new project")
# project = gl.createProject(test_project, test_group)
# print(f"Project ID: {project.id}")
# print(f"Project Wiki: {project.wiki_enabled}")
# print(f"Project Name: {project.name}")
# print(f"Project Path: {project.path}")
# print(f"Project Web URL: {project.web_url}")
# print(f"Project Wiki URL: {project.wiki_url}")
# print(f"Project Wiki Path: {project.wiki_path}")

# test_project = "test_project2"
# test_group = "test"
# group = gl.findGroup(test_group)
# print(f"Create project \{test_project}\" in group \"{test_group}\".",
#       "Print information about the new project.")
# project = gl.createProject('test_project2', group, wiki_enabled=True)
# print(f"Project ID: {project.id}")
# print(f"Project Wiki: {project.wiki_enabled}")
# print(f"Project Name: {project.name}")
# print(f"Project Path: {project.path}")
# print(f"Project Web URL: {project.web_url}")
# print(f"Project Wiki URL: {project.wiki_url}")
# print(f"Project Wiki Path: {project.wiki_path}")

# test_project = "test_project"
# test_group = "testGroup"
# print(f"Create project \"{test_project}\" in new group \"{test_group}\".",
#       "Print information about the new project.")
# project = gl.createProject(test_project, test_group)
# print(f"Project ID: {project.id}")
# print(f"Project Wiki: {project.wiki_enabled}")
# print(f"Project Name: {project.name}")
# print(f"Project Path: {project.path}")
# print(f"Project Web URL: {project.web_url}")
# print(f"Project Wiki URL: {project.wiki_url}")
# print(f"Project Wiki Path: {project.wiki_path}")

#TODO test what import_url does

# print("Attempt to create a new group \"testGroup\"")
# group = gl.createGroup('testGroup')
# print(f"Group ID: {group.id}")
# print(f"Group Name: {group.name}")
# print(f"Group Path: {group.path}")

gh_test_repo = "NOAA-GFDL/FMS"
test_group = "test"
print(f"Get the GitHub repository \"{gh_test_repo}\".")
project = gl.importGitHub(gh_test_repo, test_group)
print(f"Project ID: {project.id}")
print(f"Project Wiki: {project.wiki_enabled}")
print(f"Project Name: {project.name}")
print(f"Project Path: {project.path}")
print(f"Project Web URL: {project.web_url}")
print(f"Project Wiki URL: {project.wiki_url}")
print(f"Project Wiki Path: {project.wiki_path}")
