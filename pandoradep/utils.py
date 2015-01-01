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

    build_depends = set([])
    run_depends = set([])

    pkgs = catkin_pkg.packages.find_packages(directory, excluded)

    for pkg in pkgs:
        build_depends = build_depends.union(map(str, pkgs[pkg].build_depends))
        run_depends = run_depends.union(map(str, pkgs[pkg].exec_depends))

    return (build_depends, run_depends)


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
            if dep in repos[repo]:
                repos_to_fetch.add(repo)

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
