# Sample local_settings.py

# Github Value
github_user = 'YOUR GITHUB USER'

# Github Repo
PROJECT = "YOUR PROJECT"

REPO = '%s/%s.git' % (github_user,PROJECT)

# Here lie the Amazon secrets
AWS = {
	'secrets':{
		'aws_key' : ' __ YOUR KEY HERE __ ',
		'aws_secret' : '__ YOUR SECRET HERE ___',
		'aws_key_path' : '__ YOUR PATH HERE ___',
	}
}

localwd = '/Users/YOURREPO/'
keypath = '/Users/YOURKEY.pem'

APP = {
	'appname' : 'testapp.py'	
}



'''
'image_id' : 'ami-aecd60c7',       # Amazon Linux 64-bit
'instance_type' : 't1.micro',      # Micro Instance
'security_groups': 'default', 
'key_name': 'bckey',
'''


'''
SERVER = {
		'image_id' : AWS['defaults']['image_id'],
		'instance_type' : AWS['defaults']['instance_type'],
		'security_groups' : AWS['defaults']['security_groups'],
		'key_name' : AWS['defaults']['key_name'],
}
'''