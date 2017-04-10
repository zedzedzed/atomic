import json
import os
import subprocess


def check_make_directory(directory):
	# Create the directory if it doesn't already exist
	if not os.path.exists(directory):
		os.makedirs(directory)
		print('- Directory created')

	return


def do_git(directory, repository, reference):
	print('[*** ' + directory + ' ***]')

	check_make_directory(directory)

	# todo: how do you change from a tag release back to master in git?

	if os.path.exists(directory + '/.git/'):
		print('- Exists as a managed repository')
		try:
			#checked_out_version = subprocess.getoutput('cd ' + directory + '; git describe --tags')
			git_branch = subprocess.getoutput('cd ' + directory + '; git branch')

			if git_branch == '* master':
				if reference == 'master':
					# Should this be git fetch?
					print('- Currently on master, pulling latest changes')
					subprocess.check_output('cd ' + directory + '; git pull', shell=True)
				else:
					print('- Currently on master, changing to ' + reference)
					subprocess.check_output('cd ' + directory + '; git fetch -p; git checkout tags/' + reference, shell=True)
			else:
				checked_out_version = subprocess.getoutput('cd ' + directory + '; git describe --tags')
				if checked_out_version != reference:
					print('- Currently on ' + checked_out_version + ', changing to ' + reference)
					subprocess.check_output('cd ' + directory + '; git fetch -p; git checkout tags/' + reference, shell=True)
				else:
					print('- Already set to reference ' + reference)
					print('- No further changes required')
		except:
			print('- Could not determine current tag reference')
	else:
		# Checkout the repo
		print('- Cloning and moving to reference ' + reference)
		out = subprocess.check_output('cd ' + directory + '; git clone ' + repository + ' .', shell=True)

		# Set to a tag release if the reference is not 'master'
		if reference != 'master':
			out = subprocess.check_output('cd ' + directory + '; git checkout tags/' + reference, shell=True)

	print('\n')
	return


def do_svn(directory, repository):
	print('[*** ' + directory + ' ***]')

	check_make_directory(directory)

	if os.path.exists(directory + '/.svn/'):
		checked_out_url = subprocess.getoutput('cd ' + directory + '; svn info | awk \'/^URL/{print $2}\'')

		if checked_out_url == repository:
			print('- SVN up')
			out = subprocess.check_output('cd ' + directory + '; svn info | awk \'/^URL/{print $2}\'', shell=True)
		else:
			print('- SVN switch')
			print('  from ' + checked_out_url)
			print('  to   ' + repository)

			# Themes in https://themes.svn.wordpress.org/ produce the folllowing error when using svn switch
			# svn: E195012: Path '.' does not share common version control ancestry with the requested switch location.  Use --ignore-ancestry to disable this check.
			if 'https://themes.svn.wordpress.org/' in repository:
				svn_ignore_ancestry = '--ignore-ancestry '
			else:
				svn_ignore_ancestry = ''

			out = subprocess.check_output('cd ' + directory + '; svn sw ' + svn_ignore_ancestry + repository, shell=True)
	else:
		# Checkout the repo
		print('- SVN checkout ' + repository)
		out = subprocess.check_output('cd ' + directory + '; svn co ' + repository + ' .', shell=True)
	

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


#
# Set up core
#    "core": {
#        "repo": "https://github.com/WordPress/WordPress.git",
#        "reference": "4.7.3",
#        "install_dir": "/core"
#    },
#
do_git(pwd + specification['core']['install_dir'], specification['core']['repo'], specification['core']['reference'])


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
for component in specification['components']:
	if component.get('reference'):
		do_git(pwd + component['install_dir'] + component['name'], component['repo'], component['reference'])
	else:
		do_svn(pwd + component['install_dir'] + component['name'], component['repo'])


# Fix permissions

