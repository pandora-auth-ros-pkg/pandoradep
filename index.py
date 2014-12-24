import os
import sys

import click
import yaml
import catkin_pkg.packages

from pandoradep import utils
from pandoradep.config import colors


@click.group()
def cli():
    ''' A tiny cli tool to manage PANDORA's dependencies. '''
    pass


@cli.command()
@click.argument('root_of_pkgs', type=click.Path(exists=True, readable=True))
def create(root_of_pkgs):
    ''' Creates a repos.yml file, mapping each package to
        the corresponding repo. [used by Jenkins]
    '''

    package_dirs = {}

    for root, dirs, files in os.walk(root_of_pkgs):
        if '.git' in dirs:
            package_dirs[root] = []

    for repo in package_dirs:
        for root, dirs, files in os.walk(repo):
            if 'package.xml' in files:
                package_dirs[repo].append(os.path.basename(root))

    for repo in package_dirs:
        package_dirs[os.path.basename(repo)] = package_dirs.pop(repo)

    click.echo(package_dirs)

    with open('repos.yml', 'w') as file_handler:
        file_handler.write(yaml.dump(package_dirs))


@cli.command()
@click.argument('root', type=click.Path(exists=True, readable=True))
@click.argument('repo_name', type=click.STRING)
@click.argument('repos_file', type=click.STRING)
@click.option('--env', type=click.STRING, default='JENKINS_SCRIPTS',
              help='''Specify environmental variable for
                      the scripts. The default is JENKINS_SCRIPTS
                   ''')
def update(root, repo_name, repos_file, env):
    '''Updates dependencies [used by Jenkins]'''

    try:
        with open(repos_file, 'r') as file_handler:
            repos = yaml.safe_load(file_handler)
    except IOError, err:
        click.echo(click.style(str(err), fg=colors['error']))
        sys.exit(1)

    # Info collected from catkin packages
    catkin_output = catkin_pkg.packages.find_packages(root)

    # Just the names of the packages
    local_pkgs = [pkg.name for pkg in catkin_output.values()]

    try:
        repo_dependencies = set(repos[repo_name])
    except KeyError, err:
        click.echo(click.style(str(err) + ' not found in ' + repos_file,
                               fg=colors['error']))
        click.echo(click.style(str(repos.keys()), fg=colors['debug']))
        sys.exit(1)

    if repo_dependencies == set(local_pkgs):
        click.echo(click.style('Nothing changed', fg=colors['success']))
    else:
        click.echo(click.style('Updating packages...', fg=colors['info']))
        repos[repo_name] = local_pkgs
        utils.update_upstream(repos_file, repos, env)


@cli.command()
@click.argument('directory', type=click.Path(exists=True, readable=True))
@click.option('--build', is_flag=True,
              help='Return only the build dependencies')
@click.option('--run', is_flag=True, help='Return only the run dependencies')
@click.option('--git', is_flag=True, help='Return git repositories.')
@click.option('--save', type=click.Path(exists=True,
              resolve_path=True, writable=True),
              help='Download the dependencies in a specified directory.')
@click.option('--http', is_flag=True,
              help='Return git repos or rosinstall entries with https.')
@click.option('--exclude', '-x', multiple=True, default=None,
              type=click.Path(exists=True, readable=True),
              help='Exclude a directory from the scan.')
def scan(directory, http, exclude, git, save, build, run):
    ''' Scans the directory tree for dependencies. By default returns
        rosinstall entries that you can feed into the wstool.
    '''

    (build_depends, run_depends) = utils.get_dependencies(directory, exclude)
    depends = set(build_depends).union(run_depends)

    repos = utils.fetch_upstream()

    if build:
        utils.print_repos(build_depends, repos, http, git, save)
    elif run:
        utils.print_repos(run_depends, repos, http, git, save)
    else:
        utils.print_repos(depends, repos, http, git, save)
