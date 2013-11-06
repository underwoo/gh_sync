#!/bin/sh

# This script should be run by the git user on gitlab.
# Assume $HOME is set properly

git_repo_dir=${HOME}/repositories

for r in githubmirror/commerce-github-io.git
do
    cd ${git_repo_dir}/${r}
    if [ $? != 0 ]; then
	echo "ERROR: Unable to enter directory ${git_repo_dir}/${r}"
	exit 1
    fi

    # Check for remote
    remote_found=$( git remote -v | grep '\bgithub\b' | grep fetch | wc -l )

    if [ ${remote_found} == 0 ]; then
	echo "WARNING: No remote for repo ${git_repo_dir}/${r}.  Skipping"
	continue
    fi
    git fetch github
done
