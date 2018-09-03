#!/usr/bin/env python
import csv

import click
import jinja2
import getpass
import logging

from paramiko import SSHClient, AutoAddPolicy, AuthenticationException, SSHException
from paramiko.ssh_exception import NoValidConnectionsError

logger = logging.getLogger('default')


@click.command()
@click.option('--file', type=click.STRING,
              help='IP list input', default='list.csv')
@click.option('--patch', type=click.STRING,
              help='Name of the patch to apply', default='example.script')
@click.option('-v', '--verbose', count=True, help='Increment verbosity')
def multi_patcher_app(file, patch, verbose):
    ips = list()
    templateLoader = jinja2.FileSystemLoader(searchpath="templates/")
    templateEnv = jinja2.Environment(loader=templateLoader)
    logger.info('Going to apply patch {0}'.format(patch))
    username = input('Username: ')
    password = getpass.getpass('Password:')
    template = templateEnv.get_template(patch)

    with open(file, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for r in reader:
            ips.append(r[0])
    for ip in ips:
        click.echo('Going to patch: {0}.'.format(ip))
        patchScript = template.render(ip=ip)
        """
        # For audit purposes we can store the instantiated file
        with open('tmp/{0}.out'.format(ip), 'w') as wf:
            wf.write(patchScript)
        """
        try:
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(ip, 22, username, password, None, None, None, False, False, False)
            stdin, stdout, stderr = client.exec_command(patchScript)
            lineas = stdout.readlines()
            for l in lineas:
                click.echo(l)
        except AuthenticationException:
            logger.error('Auth error for {0}'.format(ip))
        except NoValidConnectionsError:
            logger.error('Unable to connect')
        except SSHException:
            logger.info('Connection failed for {0}'.format(ip))
        except OSError:
            logger.error('OS error, network might be unreachable. ')


if __name__ == '__main__':
    multi_patcher_app()
