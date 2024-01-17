#!/usr/bin/env python3

'''
Python script to construct a working installation of WordPress, together with plugins and themes.
Atomic acts similar to SVN:Externals and Composer.

Requires
* Python3+
* git
* svn
'''

import time
start_time = time.time()

import argparse
import json
import os
import sys
import subprocess
import shutil

count_git = 0
count_svn = 0
bad_components = []


class bcolors:
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'


def load_specification_file(specification_file):
	if os.path.isfile(specification_file):
		with open(specification_file) as spec_file:
			try:
				return json.load(spec_file)
				#print(json.dumps(specification, indent=3))
			except:
				print('Invalid json detected')
				raise	
	else:
		print('Specification file not found. Exiting.')
		exit(1)		


def check_make_directory(directory):
	# Create the directory if it doesn't already exist
	if not os.path.exists(directory):
		os.makedirs(directory)
		print('- Directory created')

	return


def get_component(needle):
	global specification
	
	for component in specification['components']:
		if needle == component['name']:
			return component 

	return False


def do_git(component):
	directory = pwd + component['install_dir']
	repository = component['repo']
	reference = component['reference']

	if 'core' != component['name']: 
		directory += component['name']

	print(bcolors.BOLD + '[*** ' + directory + ' ***]' + bcolors.ENDC)
	global count_git

	check_make_directory(directory)

	# todo: how do you change from a tag release back to master in git?

	if os.path.exists(directory + '/.git/'):
		print('- Exists as a managed GIT repository')
		try:
			#checked_out_version = subprocess.getoutput('cd ' + directory + '; git describe --tags')
			git_branch = subprocess.getoutput('cd ' + directory + '; git branch')

			if git_branch in ['* master', '* main']:
				print('- Currently on primary branch at ' + repository)

				if reference in ['master', 'main']:
					# Should this be git fetch?
					print('- Pulling latest changes')
					subprocess.check_output('cd ' + directory + '; git pull', shell=True)
				else:
					print('- Changing to reference ' + reference)
					subprocess.check_output('cd ' + directory + '; git fetch -p --tags; git checkout tags/' + reference, shell=True)
				count_git += 1
			else:
				checked_out_version = subprocess.getoutput('cd ' + directory + '; git describe --tags')
				if checked_out_version != reference:
					print('- Currently on ' + checked_out_version + ', changing to ' + reference)
					subprocess.check_output('cd ' + directory + '; git fetch -p --tags; git checkout tags/' + reference, shell=True)
					count_git += 1
				else:
					print('- Already set to reference ' + reference)
					print('- No further changes required')
		except:
			print('- Could not determine current tag reference')
	else:
		# Checkout the repo
		print('- Cloning and moving to reference ' + reference)
		try:
			if reference in ['master', 'main']:
				reference = ''
			else
				reference = '-- branch ' + reference
			out = subprocess.check_output('cd ' + directory + '; git clone ' + reference + ' --depth 1 ' + repository + ' .', shell=True)
		except subprocess.CalledProcessError as e:
			bad_components.append(component['name'])

		count_git += 1

	print('\n')
	return


def do_svn(component):
	directory = pwd + component['install_dir'] + component['name']
	repository = component['repo']

	print(bcolors.BOLD + '[*** ' + directory + ' ***]' + bcolors.ENDC)
	global count_svn
	out = ''

	check_make_directory(directory)

	if os.path.exists(directory + '/.svn/'):
		print('- Exists as a managed SVN repository')
		checked_out_url = subprocess.getoutput('cd ' + directory + '; svn info | awk \'/^URL/{print $2}\'')

		repository = repository.rstrip('/')

		if checked_out_url == repository:
			print('- SVN up with ' + repository)

			try:
				out = subprocess.check_output('cd ' + directory + '; svn up', shell=True)
			except subprocess.CalledProcessError as e:
				bad_components.append(component['name'])
		else:
			print('- SVN switch')
			print('  from ' + checked_out_url)
			print('  to   ' + repository)

			# Themes in https://themes.svn.wordpress.org/ and plugins in https://plugins.svn.wordpress.org/
			# produce the folllowing error when using svn switch
			# svn: E195012: Path '.' does not share common version control ancestry with the requested switch location.  Use --ignore-ancestry to disable this check.
			if ('://themes.svn.wordpress.org/' in repository) or ('://plugins.svn.wordpress.org/' in repository):
				svn_ignore_ancestry = '--ignore-ancestry '
			else:
				svn_ignore_ancestry = ''

			try:
				out = subprocess.check_output('cd ' + directory + '; svn sw ' + svn_ignore_ancestry + repository, shell=True)
			except subprocess.CalledProcessError as e:
				bad_components.append(component['name'])

		count_svn += 1

	else:
		# Checkout the repo
		print('- SVN checkout ' + repository)
		try:
			out = subprocess.check_output('cd ' + directory + '; svn co ' + repository + ' .', shell=True)
		except subprocess.CalledProcessError as e:
			bad_components.append(component['name'])

		count_svn += 1

	if len(out) > 0:
		print(out.decode('utf-8'))

	print('\n')
	return


def remove_component(component):
	directory = pwd + component['install_dir'] + component['name']

	if os.path.exists(directory):
		print(bcolors.BOLD + '[*** ' + directory + ' ***]' + bcolors.ENDC)

		try:
			shutil.rmtree(directory)
			print('- Successfully deleted directory')
		except OSError as e:
			print(e)
			print('- Failed to remove directory')

		print('\n')

	return


pwd = os.getcwd()
specification_file = '_specification.json'


parser = argparse.ArgumentParser()
parser.add_argument('--spec', '--specification', '--conf', '--config', help='Location of the specification json file. Defaults to _specification.json in the current directory.', action='store')
parser.add_argument('--core', help='Synchronises WordPress core', action='store_true')
parser.add_argument('-c', '--com', '--component', help='Name of component to synchronise', action='append')
args = parser.parse_args()
explicit_components = []
todo_items = {} 

if len(sys.argv) > 1:
	if args.spec != None:
		specification_file = args.spec

	specification = load_specification_file(specification_file)

	if args.core == True:
		todo_items['core'] = specification['core']

	if args.com != None:
		for arg in args.com:
			component = get_component(arg)
			if component != False:
				explicit_components.append(component)

		if len(explicit_components) > 0:
			todo_items['components'] = explicit_components
		else:
			print('No components matched specification\n')
			exit(2)

	if len(todo_items) == 0:
		todo_items = specification
else:
	specification = load_specification_file(specification_file)
	todo_items = specification



#
# Set up core
#    "core": {
#        "repo": "https://github.com/WordPress/WordPress.git",
#        "reference": "4.7.3",
#        "install_dir": "/core"
#    },
#
if todo_items.get('core'):
	do_git({
		'name': 		'core',
		'install_dir':	todo_items['core']['install_dir'],
		'repo':			todo_items['core']['repo'],
		'reference':	todo_items['core']['reference']
	})



#
# Components
#        "components": [
#        {
#            "name": "99",
#            "repo": "https://code.tss.gov.au/plugins/99.git",
#            "reference": "dev-master",
#            "install_dir": "/wp-content/plugins/"
#        },
#
if todo_items.get('components'):
	for component in todo_items['components']:
		if component.get('state') == 'removed':
			remove_component(component)
		else:
			if component.get('reference'):
				do_git(component)
			else:
				do_svn(component)


#
# What about wp-config.php?
#


#
# Fix permissions
#


#
# Output components with bad return codes
#
if len(bad_components) > 0:
	print(bcolors.FAIL)
	print('Errors encountered with the following components  :^(')
	for item in bad_components:
		print( '- ' + item )
	print('\nScroll up to view the output')
	print(bcolors.ENDC + '\n')


#
# All done
#
print('---')
print('SVN commands: %i' % count_svn)
print('GIT commands: %i' % count_git)
print('Completed in %.2f seconds\n' %(time.time() - start_time))


if len(bad_components) > 0:
	exit(10)

