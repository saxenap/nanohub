git_url = gitlab.hubzero.org
repository_url=git@gitlab.hubzero.org:saxenap/nanohub-analytics.git
temp_folder_name=temp
root_folder=~
base_folder=$(root_folder)/nanohub
env_file_path=$(base_folder)/nanoHUB/.env
env_dev_file_path=$(base_folder)/nanoHUB/.env.dev
ssh_folder_path=$(root_folder)/.ssh
ssh_config_file_path=$(ssh_folder_path)/config
ssh_public_key_path=$(ssh_folder_path)/id_rsa.pub
ssh_private_key_path=$(ssh_folder_path)/id_rsa

all: echo-vars git-setup git-repository-setup code-setup env-file-setup

echo-vars:
	@echo root_folder=$(root_folder)
	@echo base_folder=$(base_folder)
	@echo env_file_path=$(env_file_path)
	@echo env_dev_file_path=$(env_dev_file_path)
	@echo ssh_folder_path=$(ssh_folder_path)
	@echo ssh_config_file_path=$(ssh_config_file_path)
	@echo ssh_public_key_path=$(ssh_public_key_path)
	@echo ssh_private_key_path=$(ssh_private_key_path)

git-setup: git-credentials git-ssh-setup

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
	exec ssh-agent bash -c "ssh-add $(ssh_private_key_path); exec bash"
	echo "Host ${git_url}" >> $(ssh_config_file_path)
	echo "	User git" >> $(ssh_config_file_path)
	echo "	PreferredAuthentications publickey" >> $(ssh_config_file_path)
	echo "	IdentityFile ~/.ssh/id_rsa" >> $(ssh_config_file_path)
	ssh-keyscan ${git_url} >> $(ssh_folder_path)/known_hosts

code-setup:
	git clone $(repository_url) $(temp_folder_name)
	rm -rf *
	cp $(temp_folder_name)/ .

geddes-setup:
	sed -i -e "/geddes_user/ a geddes_user='${geddes_user}'" $(env_file_path)
	sed -i -e "/geddes_access_key/ a geddes_access_key='${geddes_access_key}'" $(env_file_path)
	sed -i -e "/geddes_secret_key/ a geddes_secret_key='${geddes_secret_key}'" $(env_file_path)

tunnel-setup:
	sed -i -e "/tunnel_ssh_username/ a tunnel_ssh_username='${tunnel_ssh_username}'" $(env_file_path)
	sed -i -e "/tunnel_ssh_password/ a tunnel_ssh_password='${tunnel_ssh_password}'" $(env_file_path)

db-setup:
	sed -i -e "/db_user/ a db_user='${db_user}'" $(env_file_path)
	sed -i -e "/db_password/ a db_password='${db_password}'" $(env_file_path)


copy-env-file:
	cp $(env_dev_file_path) $(env_file_path)

env-file-setup: copy-env-file geddes-setup tunnel-setup db-setup
	cat $(env_file_path)


