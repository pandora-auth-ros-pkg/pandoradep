import sys
import os
import subprocess
from subprocess import check_call
from string import Template

import yaml
import requests
import click
import catkin_pkg.packages

from pandoradep.config import PANDORA_REPO, INSTALL_TEMPLATE_SSH, \
        INSTALL_TEMPLATE_HTTPS, GIT_TEMPLATE_SSH, GIT_TEMPLATE_HTTPS, COLORS


def get_dependencies(directory, excluded=None):
    ''' Fetches all the run and build dependencies '''

    depends = []
    dep_pool = []

    pkgs = catkin_pkg.packages.find_packages(directory, excluded)

    repos = fetch_upstream()

    for pkg in pkgs:

        dep_pool = pkgs[pkg].build_depends + pkgs[pkg].exec_depends

        for dep in dep_pool:
            if pandora_lookup(dep.name, repos, with_name=False):

                current_dep = {
                        "name": dep.name,
                        "version": dep.version_eq,
                        "repo": pandora_lookup(dep.name, repos, with_name=True)
                        }

                depends = resolve_conflicts(depends, current_dep, pkg)

    return depends


def unique_depends(pkgs, identifier='name'):
    ''' Returns a set of pkgs according to their name '''

    temp = []

    for lis in pkgs:
        for dep in lis:
            temp.append(dep)

    return {v[identifier]:v for v in temp}.values()


def pandora_lookup(package_name, repo_list, with_name=False):
    ''' Checks if a package belongs to PANDORA.

        Arguments:
        package_name -- The package we are examine.
        repo_list    -- The list with the PANDORA repos
        with_name    -- If True returns the name of the repo that "package_name"
                        belongs.
        Returns:
        True or a repo name if the package_name is in the list.
        False or None if the package_name ins't in the list.

    '''

    for repo in repo_list.keys():
        if package_name in repo_list[repo]:
            if with_name:
                return repo
            else:
                return True

    if with_name:
        return None
    else:
        return False

def resolve_conflicts(old_dep_list, new_dep, package, with_warnings=True):
    ''' Checks for conflict between old and new dependencies

        Arguments:
        old_dep_list -- Dictionaries representing PANDORA packages already stored.
        new_dep      -- A dictionary with a package ready to be stored.

        Returns:
        The updated old_dep_list
    '''
    to_add = True

    if not old_dep_list:
        old_dep_list.append(new_dep)
        return old_dep_list

    for old_dep in old_dep_list:
        if old_dep['name'] == new_dep['name']:
            if old_dep['version'] != new_dep['version']:

                if with_warnings:
                    show_warnings(old_dep, new_dep, package)
                    #sys.exit(1)

                if old_dep['version'] is None:
                    old_dep['version'] = new_dep['version']
            to_add = False

        elif old_dep['repo'] == new_dep['repo']:
            if old_dep['version'] != new_dep['version']:

                if with_warnings:
                    print 'Repo'
                    show_warnings(old_dep, new_dep, package)
                    #sys.exit(1)

                if old_dep['version'] is None:
                    old_dep['version'] = new_dep['version']
                elif new_dep['version'] is None:
                    new_dep['version'] = old_dep['version']


    if to_add:
        old_dep_list.append(new_dep)

    return old_dep_list


def show_warnings(old_dep, new_dep, package):
    ''' Displays warnings and debug info about conflicts. '''

    click.echo(click.style("Package conflict in " + package,
                            fg=COLORS['warning']))
    click.echo(click.style('Info: ', fg=COLORS['debug']))
    click.echo(click.style(str(old_dep), fg=COLORS['debug']))
    click.echo(click.style(str(new_dep), fg=COLORS['debug']))



def fetch_upstream():
    ''' Returns the current pandora dependencies '''

    response = requests.get(PANDORA_REPO)

    return yaml.safe_load(response.text)


def print_repos(depends, repos, http, git, save_path):
    ''' Prints dependencies using git or rosinstall templates '''

    repos_to_fetch = set([])

    if git and http:
        template = Template(GIT_TEMPLATE_HTTPS)
    elif git:
        template = Template(GIT_TEMPLATE_SSH)
    elif http:
        template = Template(INSTALL_TEMPLATE_HTTPS)
    else:
        template = Template(INSTALL_TEMPLATE_SSH)

    for dep in depends:
        for repo in repos.keys():
            if dep['name'] in repos[repo]:
                print {"name": repo, "version": dep['version']}

    print repos_to_fetch
    sys.exit(69)

    if save_path:

        if http:
            template = Template(GIT_TEMPLATE_HTTPS)
        else:
            template = Template(GIT_TEMPLATE_SSH)

        click.echo(click.style('Saving dependencies in: ' + save_path,
                               fg=COLORS['debug']))
        click.echo()
        try:
            os.chdir(save_path)
        except OSError, err:
            click.echo(click.style(str(err), fg=COLORS['error']))
            click.echo(click.style('Invalid save path ' + save_path,
                       fg=COLORS['error']))
            sys.exit(1)

        for repo in repos_to_fetch:
            git_repo = template.substitute(repo_name=repo)
            click.echo(click.style('### Cloning ' + git_repo,
                       fg=COLORS['info']))
            try:
                check_call(['git', 'clone', git_repo])
            except subprocess.CalledProcessError, err:
                click.echo(click.style(str(err), fg=COLORS['error']))
                sys.exit(1)
    else:

        for repo in repos_to_fetch:
            click.echo(click.style(template.substitute(repo_name=repo),
                                   fg=COLORS['success']))


def update_upstream(output_file, content, env_var):
    ''' Updates upstream yaml file '''

    scripts_path = os.getenv(env_var)

    if not scripts_path:
        raise ValueError('$' + env_var + ' is not set properly.')
    try:
        os.chdir(scripts_path)
    except OSError, err:
        click.echo(click.style(str(err), fg=COLORS['error']))
        click.echo(click.style('Make sure your env is set properly.',
                               fg=COLORS['debug']))
        sys.exit(1)

    with open(output_file, 'w') as file_handler:
        file_handler.write(yaml.dump(content))

    git_commands = ["git add -u",
                    "git commit -m 'Update repos.yml'",
                    "git push origin master"
                    ]

    for cmd in git_commands:
        click.echo(click.style('+ ' + cmd, fg=COLORS['debug']))
        try:
            check_call(cmd, shell=True)
        except subprocess.CalledProcessError, err:
            click.echo(click.style(str(err), fg=COLORS['error']))
            sys.exit(1)
