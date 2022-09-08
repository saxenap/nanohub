repository_url=git@gitlab.hubzero.org:saxenap/nanohub-analytics.git
temp_folder_name=temp
root_folder="~/"
base_folder=$(root_folder)/nanohub
env_file_path=$(base_folder)/nanoHUB/.env
env_dev_file_path=$(base_folder)/nanoHUB/.env.dev

all: git-setup git-repository-setup env-file-setup

git-setup: git-credentials git-ssh-setup

git-credentials:
	git config --global user.name $(gitlab_fullname)
	git config --global user.email $(gitlab_email)
	git config --global credential.username $(gitlab_username)

git-ssh-setup:
	-rm -rf $(root_folder)/.ssh/id*
	yes '' | ssh-keygen -N '' -C $(gitlab_email) > /dev/null
	cat ~/.ssh/id_rsa.pub
	@echo "Please copy-paste the public key to your GitLab settings. Press any key to continue:" ; \
		read AGE;
	chmod 400 ~/.ssh/id_rsa.pub
	eval `ssh-agent -s`
	ssh-add ~/.ssh/id_rsa
	echo "Host gitlab.hubzero.org" >> ~/.ssh/config
	echo "User git" >> ~/.ssh/config
	echo "	PreferredAuthentications publickey" >> ~/.ssh/config
	echo "	IdentityFile ~/.ssh/id_rsa" >> ~/.ssh/config

git-repository-setup:
	git clone $(repository_url) $(temp_folder_name)

geddes-setup:
	sed -i~ '/^geddes_user=/s/=.*/="$(geddes_user)"/' $(env_file_path)
	sed -i~ '/^geddes_access_key=/s/=.*/="$(geddes_access_key)"/' $(env_file_path)
	sed -i~ '/^geddes_secret_key=/s/=.*/="$(geddes_secret_key)"/' $(env_file_path)

tunnel-setup:
	sed -i~ '/^tunnel_ssh_username=/s/=.*/="$(tunnel_ssh_username)"/' $(env_file_path)
	sed -i~ '/^tunnel_ssh_password=/s/=.*/="$(tunnel_ssh_password)"/' $(env_file_path)

db-setup:
	sed -i~ '/^db_user=/s/=.*/="$(db_user)"/' $(env_file_path)
	sed -i~ '/^db_password=/s/=.*/="$(db_password)"/' $(env_file_path)


copy-env-file:
	cp $(env_dev_file_path) $(env_file_path)

env-file-setup: copy-env-file geddes-setup tunnel-setup db-setup

