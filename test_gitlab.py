import gitlab

token = '<need_token>'

gl = gitlab.Gitlab('http://iroh.local', token)

group = gl.findGroup('gh_sync')
print group.id
print group.name
print group.path
print group.owner_id

project = gl.findProject('gh_sync', 'gh_sync')
print project.id
print project.wiki_enabled
print project.name
print project.path
print project.web_url
print project.wiki_url
print project.wiki_path

project = gl.findProject('gh_sync', group)
print project.id
print project.wiki_enabled
print project.name
print project.path
print project.web_url
print project.wiki_url
print project.wiki_path

project = gl.createProject('test_project', 'gh_sync')
print project.id
print project.wiki_enabled
print project.name
print project.path
print project.web_url
print project.wiki_url
print project.wiki_path

project = gl.createProject('test_project2', group, wiki_enabled=True)
print project.id
print project.wiki_enabled
print project.name
print project.path
print project.web_url
print project.wiki_url
print project.wiki_path

project = gl.createProject('test_project3', 'new_group')
print project.id
print project.wiki_enabled
print project.name
print project.path
print project.web_url
print project.wiki_url
print project.wiki_path
#TODO test what import_url does

# group = gl.findGroup('noGroup')
# print group.id

# group = gl.createGroup('testGroup')
# print group.id
# print group.name
# print group.path
# print group.owner_id
