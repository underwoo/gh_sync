import gitlab

from . import read_config

config = read_config.getConfig()

gl_test_project = "FMS"
gl_test_group = "NOAA-GFDL"

def test_gitlab():
    gl = gitlab.Gitlab(config['GLurl'], config['GLtoken'])
    assert isinstance(gl, gitlab.Gitlab)


def test_getGroup():
    gl = gitlab.Gitlab(config['GLurl'], config['GLtoken'])
    group = gl.findGroup(gl_test_group)
    assert isinstance(group, gitlab.gitlab.GitlabGroup)
    print(f"Group ID: {group.id}")
    assert group.id > 0
    print(f"Group Name: {group.name}")
    assert group.name == gl_test_group
    print(f"Group Path: {group.path}")
    assert group.path == gl_test_group


def test_find_nogroup():
    """This test tries to find a non-existent group.  The returned item
    should be None
    """
    gl = gitlab.Gitlab(config['GLurl'], config['GLtoken'])
    group = gl.findGroup("no_group")
    assert group is None


def test_find_project():
    """This test will pass strings as the group and project.
    The return should be a valid project (project.id > 0), and
    all other attributes should be something other than None.
    """
    gl = gitlab.Gitlab(config['GLurl'], config['GLtoken'])
    project = gl.findProject(gl_test_project, gl_test_group)
    assert isinstance(project, gitlab.gitlab.GitlabProject)
    print(f"Project ID: {project.id}")
    assert project.id > 0
    print(f"Project Wiki: {project.wiki_enabled}")
    assert project.wiki_enabled is True or project.wiki_enabled is False
    print(f"Project Name: {project.name}")
    assert project.name is not None
    print(f"Project Path: {project.path}")
    assert project.path is not None
    print(f"Project Web URL: {project.web_url}")
    assert project.web_url is not None
    print(f"Project Wiki URL: {project.wiki_url}")
    assert project.wiki_url is not None
    print(f"Project Wiki Path: {project.wiki_path}")
    assert project.wiki_path is not None


def test_find_project_group_object():
    """This test will use a group object to find the project.
    The return should be a valid project (project.id > 0), and
    all other attributes should be something other than None.
    """
    gl = gitlab.Gitlab(config['GLurl'], config['GLtoken'])
    group = gl.findGroup(gl_test_group)
    project = gl.findProject(gl_test_project, group)
    assert isinstance(project, gitlab.gitlab.GitlabProject)
    print(f"Project ID: {project.id}")
    assert project.id > 0
    print(f"Project Wiki: {project.wiki_enabled}")
    assert project.wiki_enabled is True or project.wiki_enabled is False
    print(f"Project Name: {project.name}")
    assert project.name is not None
    print(f"Project Path: {project.path}")
    assert project.path is not None
    print(f"Project Web URL: {project.web_url}")
    assert project.web_url is not None
    print(f"Project Wiki URL: {project.wiki_url}")
    assert project.wiki_url is not None
    print(f"Project Wiki Path: {project.wiki_path}")
    assert project.wiki_path is not None


def test_find_project_no_group():
    """This test will not pass a GitLab group to findProject.
    The return will be an empty GitlabProject project (project.id == -1),
    and all attributes should be None."""
    gl = gitlab.Gitlab(config['GLurl'], config['GLtoken'])
    project = gl.findProject(gl_test_project)
    print(f"Project ID: {project.id}")
    assert project.id == -1
    print(f"Project Wiki: {project.wiki_enabled}")
    assert project.wiki_enabled is False
    print(f"Project Name: {project.name}")
    assert project.name is None
    print(f"Project Path: {project.path}")
    assert project.path is None
    print(f"Project Web URL: {project.web_url}")
    assert project.web_url is None
    print(f"Project Wiki URL: {project.wiki_url}")
    assert project.wiki_url is None
    print(f"Project Wiki Path: {project.wiki_path}")
    assert project.wiki_path is None


def test_import_status_string():
    """This test will get the import status using a string for the
    GROUP/PROJECT.
    The return should not be None.
    """
    gl = gitlab.Gitlab(config['GLurl'], config['GLtoken'])
    status = gl.importStatus(f"{gl_test_group}/{gl_test_project}")
    assert status is not None


def test_import_status_project():
    """This test will get the import status using a project
    object.
    The return should not be None."""
    gl = gitlab.Gitlab(config['GLurl'], config['GLtoken'])
    project = gl.findProject(gl_test_project, gl_test_group)
    status = gl.importStatus(project)
    assert status is not None
