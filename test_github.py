import github

token = "<need_token>"
gh = github.Github(token=token)

repos = gh.getRepos(name="CommerceGov", type="orgs")

for r in repos:
    print r.name, r.ssh_url, r.has_wiki, r.wiki_url
