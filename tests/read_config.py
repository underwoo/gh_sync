import configparser
import os
import sys

def readConfig(configFile='~/.ghsyncrc'):
    print(f"Reading configuration file \"{configFile}\"",
          file=sys.stderr)
    config = configparser.ConfigParser()
    config.read(configFile)

    # Read in core options
    conf = {}
    conf['githuborg'] = config.get('global','gitHubOrgName')
    conf['gitlaborg'] = config.get('global','gitLabNSpace')
    conf['gitlabRepoBase'] = config.get('global','gitLabRepos')
    conf['GHtoken'] = config.get('global','gitHubToken')
    conf['GLtoken'] = config.get('global','gitLabToken')
    conf['GLurl'] = config.get('global','gitLabUrl')
    conf['logDir'] = config.get('global','logDir')

    return conf


def getEnv(env_var):
    try:
        if os.getenv(env_var, None) is not None:
            return os.getenv(env_var)
    except Exception as err:
        print(f"Error reading environment variable \"{env_var}\": {err}",
              file=sys.stderr)
        raise
    return None

def getConfig():
    # Looking for multiple configuration files in the following order.
    # The first file found will be used:
    #
    #   - gh_sync.conf in the current directory
    #   - $HOME/.gitlabsyncrc
    #
    # The following Environment Variables will override the
    # configuration files
    #
    #   - GHSYNC_GITLAB_URL
    #   - GHSYNC_GITLAB_TOKEN
    #   - GHSYNC_GITLAB_GROUP
    #   - GHSYNC_GITHUB_ORG
    #   - GHSYNC_GITHUB_TOKEN
    #   - GHSYNC_LOGDIR

    # The only default value in the configuration is th log directory
    config = {
        "githuborg":  None,
        "gitlaborg":  None,
        "gitlabRepoBase":  None,
        "GHtoken":  None,
        "GLtoken":  None,
        "GLurl":  None,
        "logDir": os.getcwd()}
    if os.path.exists(os.path.join(os.getcwd(), "gh_sync.conf")):
        config = readConfig(os.path.join(os.getcwd(), "gh_sync.conf"))
    elif os.path.exists(os.path.join(os.path.expanduser("~"), ".ghsyncrc")):
        config = readConfig(os.path.join(os.path.expanduser("~"), ".ghsyncrc"))
    # Override anything from the environment
    config['GLurl'] = getEnv("GHSYNC_GITLAB_URL") or config['GLurl']
    config['GLtoken'] = getEnv("GHSYNC_GITLAB_TOKEN") or config['GLtoken']
    config['gitlaborg'] = getEnv("GHSYNC_GITLAB_GROUP") or config['gitlaborg']
    config['githuborg'] = getEnv("GHSYNC_GITHUB_ORG") or config['githuborg']
    config['GHtoken'] = getEnv("GHSYNC_GITHUB_TOKEN") or config['GHtoken']
    config['logDir'] = getEnv("GHSYNC_LOGDIR") or config['logDir']

    return config