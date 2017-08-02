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

count_git = 0
count_svn = 0


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


def do_git(directory, repository, reference):
	print('[*** ' + directory + ' ***]')
	global count_git

	check_make_directory(directory)

	# todo: how do you change from a tag release back to master in git?

	if os.path.exists(directory + '/.git/'):
		print('- Exists as a managed GIT repository')
		try:
			#checked_out_version = subprocess.getoutput('cd ' + directory + '; git describe --tags')
			git_branch = subprocess.getoutput('cd ' + directory + '; git branch')

			if git_branch == '* master':
				print('- Currently on master at ' + repository)

				if reference == 'master':
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
		out = subprocess.check_output('cd ' + directory + '; git clone ' + repository + ' .', shell=True)
		count_git += 1

		# Set to a tag release if the reference is not 'master'
		if reference != 'master':
			out = subprocess.check_output('cd ' + directory + '; git checkout tags/' + reference, shell=True)
			count_git += 1

	print('\n')
	return


def do_svn(directory, repository):
	print('[*** ' + directory + ' ***]')
	global count_svn

	check_make_directory(directory)

	if os.path.exists(directory + '/.svn/'):
		print('- Exists as a managed SVN repository')
		checked_out_url = subprocess.getoutput('cd ' + directory + '; svn info | awk \'/^URL/{print $2}\'')

		repository = repository.rstrip('/')

		if checked_out_url == repository:
			print('- SVN up with ' + repository)
			out = subprocess.getoutput('cd ' + directory + '; svn up')
		else:
			print('- SVN switch')
			print('  from ' + checked_out_url)
			print('  to   ' + repository)

			# Themes in https://themes.svn.wordpress.org/ and plugins in https://plugins.svn.wordpress.org/
			# produce the folllowing error when using svn switch
			# svn: E195012: Path '.' does not share common version control ancestry with the requested switch location.  Use --ignore-ancestry to disable this check.
			if ('https://themes.svn.wordpress.org/' in repository) or ('https://plugins.svn.wordpress.org/' in repository):
				svn_ignore_ancestry = '--ignore-ancestry '
			else:
				svn_ignore_ancestry = ''

			out = subprocess.getoutput('cd ' + directory + '; svn sw ' + svn_ignore_ancestry + repository)

		count_svn += 1

		if len(out) > 0:
			print(out) 
	else:
		# Checkout the repo
		print('- SVN checkout ' + repository)
		out = subprocess.check_output('cd ' + directory + '; svn co ' + repository + ' .', shell=True)
		count_svn += 1
	

	print('\n')
	return



pwd = os.getcwd()

with open('_specification.json') as spec_file:
	try:
		specification = json.load(spec_file)
	except:
		print('Invalid json detected')
		raise

#print(json.dumps(specification, indent=3))


parser = argparse.ArgumentParser()
parser.add_argument('--core', help='Synchronises WordPress core', action='store_true')
parser.add_argument('-c', '--com', '--component', help='Name of component to synchronise', action='append')
args = parser.parse_args()
explicit_components = []
todo_items = {} 

if len(sys.argv) > 1:
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
else:
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
	do_git(pwd + todo_items['core']['install_dir'], todo_items['core']['repo'], todo_items['core']['reference'])



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
		if component.get('reference'):
			do_git(pwd + component['install_dir'] + component['name'], component['repo'], component['reference'])
		else:
			do_svn(pwd + component['install_dir'] + component['name'], component['repo'])


#
# What about wp-config.php?
#


#
# Fix permissions
#


#
# All done
#
print('---')
print('SVN commands: %i' % count_svn)
print('GIT commands: %i' % count_git)
print('Completed in %.2f seconds\n' %(time.time() - start_time))

