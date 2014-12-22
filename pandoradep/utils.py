import sys
import os
import subprocess
from subprocess import check_call, CalledProcessError
from string import Template

import yaml
import requests
import click
import catkin_pkg.packages

from config import PANDORA_REPO, INSTALL_TEMPLATE_SSH, INSTALL_TEMPLATE_HTTPS, \
    GIT_TEMPLATE_SSH, GIT_TEMPLATE_HTTPS, colors


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

    r = requests.get(PANDORA_REPO)

    return yaml.safe_load(r.text)


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
        for repo, packages, in repos.items():
            for package in packages:
                if dep == package:
                    repos_to_fetch.add(repo)

    if save_path:

        if http:
            template = Template(GIT_TEMPLATE_HTTPS)
        else:
            template = Template(GIT_TEMPLATE_SSH)

        click.echo(click.style('Saving dependencies in: ' + save_path,
                               fg=colors['debug']))
        click.echo()
        try:
            os.chdir(save_path)
        except OSError:
            click.echo(click.style('Invalid save path ' + save_path,
                       fg=colors['error']))

        for repo in repos_to_fetch:
            git_repo = template.substitute(repo_name=repo)
            click.echo(click.style('### Cloning ' + git_repo,
                       fg=colors['info']))
            try:
                check_call(['git', 'clone', git_repo])
            except subprocess.CalledProcessError:
                pass
    else:

        for repo in repos_to_fetch:
            click.echo(click.style(template.substitute(repo_name=repo),
                                   fg=colors['success']))


def update_upstream(output_file, content, env_var):
    ''' Updates upstream yaml file '''

    with open(output_file, 'w') as f:
        f.write(yaml.dump(content))

    scripts_path = os.getenv(env_var)

    if not scripts_path:
        raise ValueError('$' + env_var + ' is not set properly.')
    try:
        os.chdir(scripts_path)
    except OSError:
        click.echo(click.style('Error: Make sure your enviroment is set properly',
                   fg=colors['error']))

    git_commands = ["git add -u",
                    "git commit -m 'Update repos.yml'",
                    "git push origin master"
                    ]

    for cmd in git_commands:
        click.echo(click.style('+ ' + cmd, fg=colors['debug']))
        try:
            check_call(cmd, shell=True)
        except subprocess.CalledProcessError:
            click.echo(click.style('Error: ' + cmd, fg=colors['error']))
