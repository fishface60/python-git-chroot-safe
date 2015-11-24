#!/usr/bin/python

'''Run a shell in a repo made chroot safe with sandbox
'''

from gitchrootsafe import make_chroot_safe
import sandboxlib

from argparse import ArgumentParser, REMAINDER
from os.path import abspath, join, relpath
from subprocess import check_call


parser = ArgumentParser(description=__doc__)
parser.add_argument("--root", default="/")
parser.add_argument("command", nargs=REMAINDER)

args = parser.parse_args()


repository = "."
root = args.root
command = args.command or ['bash']

def root_relative(path):
	return join("/", relpath(abspath(path), root))

with make_chroot_safe(repository=repository, root=root) as (binds, protects):
	mounts = [
		('proc', "/proc", 'proc', None),
	]
	for src, dest in binds:
		mounts.append((src, root_relative(dest), None, "bind"))
	for path in protects:
		mounts.append((None, root_relative(path), None, "remount,bind,ro"))
	executor = sandboxlib.executor_for_platform()
	executor.run_sandbox(command=command, cwd=root_relative(repository),
	                     filesystem_root=root,
	                     extra_mounts=mounts, stdout=None, stderr=None)
