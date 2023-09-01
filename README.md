# nanoHUB

### Required Access:

For Mac and Windows

1. [Code repository for nanoHUB Analytics](https://gitlab.hubzero.org/saxenap/nanohub-analytics) on HubZero's GitLab
   1. This access is provided by Pascal. You will need to share:
      1. The email address you want to use for GitLab. 
      2. The ssh public key you want to use.
   2. Use this email address to [create a new account on GitLab](https://gitlab.com/users/sign_up/).
2. Server Access
   1. These are db2, db3, db4... db(n) and compute01... compute0(n). 
   2. Access to these is granted by Pascal. You will need to share:
         1. Your Purdue career account username.
         2. The ssh public key you want to use.
   3. Configuration & Credentials to use once access granted:
      1. Hostname: db(n).nanohub.org (Example: for db3, the hostname will be db3.nanohub.org)
      2. Username: Purdue Career Account Username
      3. Password: Purdue Career Account Password (not BoilerKey)
3. Database(SQL<sup>)1,2</sup> Access
   1. db2, db3, db4... db(n)
   2. The databases run on their respective servers. 
      Example: db2 database runs on db2 server from 2 above.
   3. Access to these is granted by Pascal.
   
4. Geddes<sup>3</sup>
   1. This access is provided by ITap.
   
5. VPN 
   1. All Purdue staff and students should have access to Purdue's VPN already.
   2. [Download](https://www.itap.purdue.edu/services/software.html) Purdue specific VPN software.
      1. Make sure to select the appropriate option for your machine (personal or Purdue provided).
      2. Only install VPN/Core!
   3. Configuration & Credentials:
      1. Address: webvpn2.purdue.edu
      2. Username: Purdue Username
      3. Password: ******

--------

### Required Downloads/Installs on your machine:
1. Docker<sup>4</sup>
   1. Install for [Terminal/Shell](https://docs.docker.com/get-docker/)
   2. Install for Desktop
   3. Additional Guidance (Windows)
         1. For docker, you must have virtualization enabled in BIOS
            1. Called different things for different manufacturers
            2. Google to find yours
               1. Example: ASUS = "SVM Mode"
         2. You will also need a 64 bit machine (x64 architecture, or ARM64 works as well) in order to install the WSL 2 Linux kernel. 
      You can use a x86 (32 bit) processor, however you are extremely limited in what images you can download (this does not matter for mac because they emulate x64).
         3. In order for docker to work, we will need to install Make on Windows. We will do this [via MinGW](https://www.youtube.com/watch?v=taCJhnBXG_w).
            1. Shell used in video: Git
         4. Once Make is installed, navigate to the folder with the root of the nanoHUB repository (what you cloned to) with shell.
            1. Once in destination, make sure of the following:
               1. You should see "MINGW64" or similar behind your name/id depending on what architecture you are.
               2. Run the command "mingw32-make"
                  1. The result should be "cp nanoHUB/.env.dev nanoHUB/.env"
2. Git<sup>5</sup>
   1. Install for [Terminal/Shell](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
   2. (Optional for mac) Install for [Desktop](https://git-scm.com/downloads/guis)
3. VPN (see #5 above)
   1. Only install VPN/Core!
4. (Optional for mac) IDE<sup>6</sup>
   1. You have many choices:
      1. (Recommended) [PyCharm](https://www.jetbrains.com/pycharm/)
         1. PyCharm is a professional IDE but available for free to students.
         2. It is used by the nanoHUB-analytics team.  
         3. The whole JetBrains suite is [available through your purdue.edu email](https://www.jetbrains.com/community/education/#students).
      2. [Sublime Text 3](https://www.sublimetext.com) (note: requires lots of setup to be IDE)
      3. [Visual Studio Code](https://visualstudio.microsoft.com/vs/)
      4. [vim](https://www.vim.org) (available by default on most machines, lacks features)
      5. [Spyder](https://www.spyder-ide.org)

--------

### Database Access

Credentials to use once access granted:
1. Log in to the respective server from 2 above. 
2. Your database credentials are stored in a _.my.cnf_ file in your root directory on that server.
   1. SSH into the respective server (db3.nanohub.org etc.). In your terminal or command line, type:
   ```shell
   ssh db3.nanohub.org -l PurdueCareerAccountUSERNAME
   ```    
   2. Once logged in to the remote server (db3 in this case), type:
   ```shell
   cd ~/   
   nano .my.cnf
   ```
   3. Once logged in to the remote server:
   
      1. username:
      ```shell
         awk '/^user/ {print $3; exit}' .my.cnf
      ```
      2. password: 
      ```shell
         awk '/^password/ {print $3; exit}' .my.cnf
      ```
      
      Note: All of this can be done manually as well (EG. "ls -lf", "cd .my.cnf", "vim .my.cnf")

[//]: # (Note: to list the files here, use:)

[//]: # (   ```)

[//]: # (   ls -lf)

[//]: # (   ```)

[//]: # (   This shows hidden files.)

[//]: # ()
[//]: # (Note: You can also extract your username and password using VIM to open .my.cnf)

3. To access the database:
   1. Direct access:
      1. SSH into the respective server (db3.nanohub.org etc.). In your terminal or command line, type:
      ```shell 
      ssh db3.nanohub.org -l PurdueCareerAccountUSERNAME
      ```
      3. Once logged in to the remote server (db3 in this case), type:
      ```shell
      mysql
      ```
   2. Access via code:
      1. Create an ssh tunnel to the remote server.
      2. Make database calls as needed.
4. To build the container
   1. Mac: your .env is filled out with the two user/pass combinations you need, you can run "make dev" and your container should build. To clean, run "make clean".
   2. Windows: there are a few changes we need to make before we can run our make command.
      1. Open up the Makefile
      2. Under "make dev"
         1. “make dev-down” -> “mingw32-make dev-down”
         2. “make dev-up” -> “mingw32-make dev-up”
      3. To run: "mingw32-make dev"
         1. Once built, it will say that it cannot find a default browser. This is fine, just go to your browser of choice and type "127.0.0.1/lab" in the address bar.
         2. Password: nanoHUB
      4. To clean: "mingw32-make clean"
   3. Note for both: Run the clean after each pull or any errors.

--------

**Footnotes:**

1. Database Information:
   1. nanoHUB uses [MariaDB](https://mariadb.com). This is an open-source relational database management system (DBMS) that is a compatible drop-in replacement for the widely used MySQL database technology. Database management system is used to store and manage data.
   2. The current version in use is: Ver 15.1 Distrib 5.5.68-MariaDB, for Linux (x86_64) using readline 5.1

2. Database Servers:
   1. db1: Main Production line for the nanoHUB database (No access required/granted)
   2. db2: A copy of the main production nanoHUB. It is used as a pipeline only. No analytics work is performed (access required / provided). You will need access to db2 as well as server access to db2. This is done via SSH. In order to begin working, this is the most important step to get access for. 
   3. db3: A copy for the db2. It is used for analytics purposes. (Access required/ provided)
   4. db4: It is a copy of db2 as well. Running on Geddes. This is to be used for the analytics work (access required / provided).

3. Geddes Object Storage:

[Object storage](https://www.youtube.com/watch?v=71iiAzlF2Rs) is a way of storing large unstructured big data. It is different from the traditional file storage system which is found on computers. Gedges Object Storage is similar to AWS S3, google cloud. In order to access the stored data one needs to use the specific file paths.

4. Docker:

Docker is an open-source platform for deploying and managing containerized applications. A container is a standard unit of software that packages up code and all its dependencies, so the application runs quickly and reliably from one computing environment to another.
Users need to [have basic understanding](https://www.docker.com/resources/what-container/) of dockers and be able to run the nanohub-analytics containers successfully on
their machines.

5. Git:

Git is an open-source software for tracking changes to a project. 
It is the main way to collaborate in the coding world in a way that protects what each person works on. 
If there is an issue, anyone in the repository (where you work on a specific project) is able to pull (download) a prior version to either have a working version or a new starting point.
6. IDE:

IDE stands for integrated development environment. This is where code is developed (for the most part). IDE's are also known to have many useful features beyond basic coding, such as having an onboard way to run code, syntax completion, and more.
It is able to tell you where you made a mistake in your code, as well as quickly provide useful info about libraries you may want to use. For our purposes, we will be using it with the code on GitLab in order to trace function calls back to their functions, which would be almost impossible without an IDE. 
The IDE allows us to just hover over a function and find its location, while in Jupyter you must browse through every file to find the function you are looking for.
