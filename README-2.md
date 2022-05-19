# nanoHUB

### Required Access:

1. [Code repository for nanoHUB Analytics](https://gitlab.hubzero.org/saxenap/nanohub-analytics) on HubZero's GitLab
   1. This access is provided by [Pascal](mailto:pmeunier@ucsd.edu). You will need to share:
      1. The email address you want to use for GitLab. 
      2. The ssh public key you want to use.
   2. Use this email address to [create a new account on GitLab](https://gitlab.com/users/sign_up/).
2. Server Access
   1. These are db2, db3, db4... db(n) and compute01... compute0(n). 
   2. Access to these is granted by [Pascal](mailto:pmeunier@ucsd.edu). You will need to share:
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
   3. Access to these is granted by [Pascal](mailto:pmeunier@ucsd.edu).
   
4. Geddes<sup>3</sup>
   1. This access is provided by ITap.
   
5. VPN 
   1. All Purdue staff and students should have access to Purdue's VPN already.
   2. [Download](https://www.itap.purdue.edu/services/software.html) Purdue specific VPN software.
      1. Make sure to select the appropriate option for your machine (personal or Purdue provided).
   3. Configuration & Credentials:
      1. Address: webvpn2.purdue.edu
      2. Username: Purdue Username
      3. Password: BoilerKey

--------

### Required Downloads/Installs on your machine:
1. Docker<sup>4</sup>
   1. Install for [Terminal/Shell](https://docs.docker.com/get-docker/)
   2. Install for Desktop
2. Git<sup>5</sup>
   1. Install for [Terminal/Shell](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
   2. (Optional) Install for [Desktop](https://git-scm.com/downloads/guis)
3. VPN (see #5 above)
4. (Optional) IDE
   1. You have many choices:
      1. (Recommended) [PyCharm](https://www.jetbrains.com/pycharm/)
         1. PyCharm is a professional IDE but available for free to students.
         2. It is used by the nanoHUB-analytics team.  
      2. [Sublime Text 3](https://www.sublimetext.com)
      3. [Visual Studio Code](https://visualstudio.microsoft.com/vs/)
      4. [vim](https://www.vim.org)
      5. [Spyder](https://www.spyder-ide.org)

--------

### Database Access

Credentials to use once access granted:
1. Log in to the respective server from 2 above. 
2. Your database credentials are stored in a _.my.cnf_ file in your root directory on that server.
   1. SSH into the respective server (db3.nanohub.org etc.). In your terminal or command line, type:
```shell
ssh db3.nanohub.org -l PurdueCareerAccountUSERNAMEx
```    
Once logged in to the remote server (db3 in this case), type:
```shell
cd ~/   
nano .my.cnf
```
2. You can also directly extract your username and password. Once logged in to the remote server:
   1. For username:
```shell
awk '/^user/ {print $3; exit}' .my.cnf
```
   2. For password:
```shell
awk '/^password/ {print $3; exit}' .my.cnf
```
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
Object storage is a way of storing large unstructured big data. It is different from the traditional file storage system which is found on computers. https://www.youtube.com/watch?v=71iiAzlF2Rs
Gedges Object Storage is similar to AWS S3, google cloud. In order to access the stored data one needs to use the specific file paths.

4. Docker:
Docker is an open-source platform for deploying and managing containerized applications. A container is a standard unit of software that packages up code and all its dependencies, so the application runs quickly and reliably from one computing environment to another. https://www.docker.com/resources/what-container/
-Users need to understand basic understanding of dockers and be able to run the nanohub-analytics containers successfully on
their machines.

5. Git
6. IDE
