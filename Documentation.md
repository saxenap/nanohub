# Nanohub Documentation Overview

* Cloned the repository
* Built the Docker
* Added Custom Environment Variables
* Opened Jupyter Lab

## Resources Used
* Docker Desktop Engine Version 20.10.7
* Github: https://github.com/saxenap/nanohub.git

## Step1: Clone the repository 
1. Navigate to the mainpage of the Github repository
2. Clone the HTTPS / Copy the URL Link
![HTTPS](https://user-images.githubusercontent.com/71523797/122682044-e6225a80-d1bc-11eb-970e-a1543f1cef23.png)
4. To Copy and sync the existing repository into a new location(your computer), in a new terminal, use `git clone` and paste the URL Link

## Step2-1: Build the Docker
1. In the same Terminal, use `docker-compose up --build` to aggregate the output of each containers
2. Copy and Paste the Server URL into your browser
![JupyterLab](https://user-images.githubusercontent.com/71523797/122682189-9db76c80-d1bd-11eb-8568-b8096a65a137.png)
5. Use `CTRL+C` to stop running the docker

## Step2-2: Build the Updated Docker 
1. In the same Terminal, use `git pull origin` to aggregate the new changes you made
2. In the same Terminal, use `docker-compose up --build` to update the old containers with new changes
3. Reopen the new Server URL in your browser 

## Step3: Add Custom Environment Variables
*Open the VPN if you are off campus
1. Open a new Terminal, use `cd nanoHUB` to move the nanoHUB directory upwards
2. Use `ls -la` to list all file contents of the directory (including the hidden contents)
3. Use `cp. env.dev .env` to copy the content from the en.dev file into a new .env file
4. Use `nano .env` to open the new created .env file as a editor window
5. Enter your ssh and nanohub's username and password to edit the file
![password](https://user-images.githubusercontent.com/71523797/122682485-34d0f400-d1bf-11eb-9996-e4ce05d7a87f.png)
6. Use `CTRL+X` to exit the setting
7. To check if you save the username and password, use `nano .env` to reopen the editor window

## Step4: Open Jupyter Lab
1. Return to the Step2 Terminal, use `docker-compose up --build` to open the new Server URL
2. Open the file `pipeline/salesforce/_task_test.ipynb` in the browser
3. Run the code to see the dataset 


# Potential Errors

## Docker
1. `docker.errors.DockerException: Error while fetching server API version: ('Connection aborted.', ConnectionRefusedError(61, 'Connection refused'))`
    
    * This could mean your Docker engine (and Docker Desktop, if applicable) is turned off. 





