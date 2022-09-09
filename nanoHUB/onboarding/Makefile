git_url = gitlab.hubzero.org
repository_url=git@gitlab.hubzero.org:saxenap/nanohub-analytics.git
root_folder=~
temp_folder_path=$(root_folder)/temp
base_folder=$(root_folder)/nanohub
env_file_path=$(base_folder)/nanoHUB/.env
env_dev_file_path=$(base_folder)/nanoHUB/.env.dev
ssh_folder_path=$(root_folder)/.ssh
ssh_config_file_path=$(ssh_folder_path)/config
ssh_public_key_path=$(ssh_folder_path)/id_rsa.pub
ssh_private_key_path=$(ssh_folder_path)/id_rsa

gitlab_fullname = $(fullname)
gitlab_email = $(purdue_email)
gitlab_username = $(purdue_career_username)
geddes_user = $(purdue_career_username)
tunnel_ssh_username = $(purdue_career_username)
tunnel_ssh_password = $(purdue_career_password)

mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))



define replace_in_file
sed -i 's/${2}/${3}/' {1}
endef

define replace_in_env_file
$(call replace_in_file, ${env_file_path}, ${1}, ${2})
endef

##help
##help make: Setup the user with their credentials on this machine for use with nanoHUB Analytics GitLab, databases, and other infrastructure.
##help
##help Arguments:
##help 1. fullname - Don't forget to use quotes around your name (Example: fullname="data god")
##help 2. purdue_email - This is the email you used to register with gitlab.hubzero.org. Usually, is your Purdue email. (Example: purdue_email=datagod@purdue.edu)
##help 3. purdue_career_username - This is your preferred username to use with Git. Usually, this would just be your Purdue Career Account username. (Example: purdue_career_username=datagod)
##help 4. purdue_career_password (Example: purdue_career_password=*********)
##help 5. geddes_access_key (Example: geddes_access_key=*********)
##help 6. geddes_secret_key (Example: geddes_secret_key=******************)
##help 7. db_user
##help 8. db_password
##help
##help
##help During setup, the program will pause to provide you with a SSH public key. Here's what you need to do with it:
##help 1. Copy the provided public key
##help 2. Visit https://gitlab.hubzero.org/-/profile/keys
##help 3. Paste the public key into the box and give it a name such as 'geddes'
##help 4. Click on 'Add Key'
##help 5. Come back to the terminal on Jupyter and click 'Enter'
##help
##help
##help Once the program completes setup, you are ready to start using the machine.
##help Good luck, and may the data force be with you.
##help
##help ##################################################################################
##help d##################################################################################
.DEFAULT_GOAL := all
all: final

dev-all: echo-vars all

####################################################################################

echo-vars:
	@echo root_folder=$(root_folder)
	@echo base_folder=$(base_folder)
	@echo env_file_path=$(env_file_path)
	@echo env_dev_file_path=$(env_dev_file_path)
	@echo ssh_folder_path=$(ssh_folder_path)
	@echo ssh_config_file_path=$(ssh_config_file_path)
	@echo ssh_public_key_path=$(ssh_public_key_path)
	@echo ssh_private_key_path=$(ssh_private_key_path)

####################################################################################

git-setup: git-credentials git-ssh-setup gitlab-config

git-credentials:
	git config --global user.name $(gitlab_fullname)
	git config --global user.email $(gitlab_email)
	git config --global credential.username $(gitlab_username)


git-ssh-setup:
	-rm -rf $(ssh_folder_path)/id*
	yes '' | ssh-keygen -N '' -C $(gitlab_email) > /dev/null
	cat $(ssh_public_key_path)
	@echo "Please copy-paste the public key to your GitLab settings. Press any key to continue:" ; \
		read AGE;
	#eval $(ssh-agent -s)
	#ssh-add $(ssh_private_key_path)
	exec ssh-agent bash -c "ssh-add $(ssh_private_key_path); exec bash"

gitlab-config:
	echo "Host ${git_url}" >> $(ssh_config_file_path)
	echo "	User git" >> $(ssh_config_file_path)
	echo "	PreferredAuthentications publickey" >> $(ssh_config_file_path)
	echo "	IdentityFile ~/.ssh/id_rsa" >> $(ssh_config_file_path)
	echo "	StrictHostKeyChecking no" >> $(ssh_config_file_path)
	echo "	UserKnownHostsFile /dev/null" >> $(ssh_config_file_path)
	echo "	AddKeysToAgent yes" >> $(ssh_config_file_path)

####################################################################################

code-setup: git-setup
	git clone $(repository_url) $(temp_folder_path)
	rm -rf *
	cp -r $(temp_folder_path)/ .

####################################################################################

env-file-setup: code-setup copy-env-file geddes-setup tunnel-setup db-setup
	cat $(env_file_path)

copy-env-file:
	cp $(env_dev_file_path) $(env_file_path)

geddes-setup:
	$(call replace_in_env_file, {GEDDES_USERNAME_HERE}, ${geddes_user})
	$(call replace_in_env_file, {GEDDES_ACCESS_KEY_HERE}, ${geddes_access_key})
	$(call replace_in_env_file, {GEDDES_SECRET_KEY_HERE}, ${geddes_secret_key})

tunnel-setup:
	$(call replace_in_env_file, {CAREER_ACCOUNT_USERNAME_HERE}, ${tunnel_ssh_username})
	$(call replace_in_env_file, {CAREER_ACCOUNT_PASSWORD_HERE}, ${tunnel_ssh_password})

db-setup:
	$(call replace_in_env_file, {DB_USERNAME_HERE}, ${db_user})
	$(call replace_in_env_file, {DB_PASSWORD_HERE}, ${db_password})

####################################################################################

final: env-file-setup

####################################################################################

help : Makefile
	@sed -n 's/^##help//p' ${mkfile_path}
	@echo "\n"