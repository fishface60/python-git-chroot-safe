#!/usr/bin/python

from contextlib import contextmanager
from os.path import exists, join, relpath
from shutil import rmtree
from subprocess import check_call, check_output
from tempfile import NamedTemporaryFile, mkdtemp


@contextmanager
def _tempdir(*args, **kwargs):
	td = mkdtemp(*args, **kwargs)
	try:
		yield td
	finally:
		rmtree(td)


def _parse_alternates_paths(objectsdir):
	alternates = join(objectsdir, 'info', 'alternates')
	if not exists(alternates):
		return ()
	return (p.rstrip('\n') for p in open(alternates, 'r') if p)


@contextmanager
def make_chroot_safe(repository='.', root='/'):
	gitdir = check_output(['git', 'rev-parse', '--git-dir'],
	                      cwd=repository).strip()
	objects = join(gitdir, 'objects')
	stores = list(_parse_alternates_paths(objects))
	if not stores:
		yield ((), ())
	with _tempdir(dir=objects, prefix='chroot-safe-') as td:
		binds = []
		protects = []
		with NamedTemporaryFile(dir=td, delete=False,
		                        prefix='new-alternates-') as f:
			for store in stores:
				binddest = mkdtemp(dir=td, prefix='objects-')
				binds.append((store, binddest))
				protects.append(binddest)
				f.write(relpath(binddest, objects) + '\n')
		binds.append((f.name, join(objects, 'info', 'alternates')))
		yield (binds, protects)
