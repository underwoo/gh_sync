#!/bin/sh

# this script will mirror github repos on gitlab.  All that is needed
# is a list of repos to mirror.
#
# Currently the list will be manually given.  At a later day, I will
# use the github API to get a list of repos to mirror.  (I also need
# to figure out if there is a way to automatically create repos on
# gitlab.)

mirror_repo_base="/nbhome/Seth.Underwood/gitMirrors"

for r in 'CommerceGov.github.io'
#           noaa-gfdl-mom6 )
do
    cd ${mirror_repo_base}
    pwd
    # Do we need a clone?
    if [ ! -e ${r}.git ]; then
	git clone --mirror githubmirror:CommerceGov/${r}
	if [ $? != 0 ]; then
	    echo "ERROR cloning repository."
	    exit 1
	fi
    fi
    pwd
    cd ${r}.git

    # Check for the origin (pull) remote, and verify it is github
    origin_host=$( git remote -v | grep origin | grep fetch | cut -f 2 | cut -d ':' -f 1 )

    if [ ! ${origin_host}X = 'githubmirrorX' -a ! ${origin_host}X = 'git@github.comX' ]; then
	echo "ERROR: Remote host listed as origin is not correct."
	echo "ERROR: Expected 'githubmirror' or 'git@github.com', but got ${origin_host}."
	echo "ERROR: Mirror not performed."
	continue
    fi
    
    # Check if gitlab origin is found.  If not, add
    gitlab_remote_found=$( git remote -v | grep '\bgitlab\b' | grep fetch | wc -l )

    if [ ${gitlab_remote_found} != 1 ]; then
	gitlab_repo=$( echo ${r} | tr '[:upper:]' '[:lower:]' )
	gitlab_repo=$( echo ${gitlab_repo} | tr '.' '-' )
	git remote add gitlab gitlabmirror:seth.underwood/${gitlab_repo}.git
    fi

    # Fetch updates from github
    git fetch origin
    git fetch -t origin

    # Push updates to gitlab
    git push --all gitlab
    git push --tags gitlab
done

    
