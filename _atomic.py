import json
import os
import subprocess

def do_git(directory, repository, reference):
	print('[*** ' + directory + ' ***]')

	# Create the directory if it doesn't already exist
	if not os.path.exists(directory):
		os.makedirs(directory)
		print('- Directory created')

	# todo: how do you change from a tag release back to master in git?

	if os.path.exists(directory + '/.git/'):
		#subprocess.check_output('cd ' + directory + '; git rev-parse --is-inside-work-tree', shell=True)
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
		print('svn')


# Fix permissions

