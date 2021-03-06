Deployment
==========

# Update the AWS rabbitmq instance 
**NOTE:** This section applies if adding a new Bioconductor Build server.

Login to AWS, Navigate to Instances, click on rabbitmq. In the details section
on the bottom, navigate to Security groups and click on stomp. Add the new
server's external IP address to the Inbound.

# Linux/MAC Install : 

All steps should be performed as user `pkgbuild` unless otherwise noted.

#### Clone Repositories

```
git clone https://github.com/Bioconductor/packagebuilder.git
git clone git@github.com:Bioconductor/bioc-common-python.git
cd packagebuilder
```

#### Set Up Virtual Envirnment and Install Dependencies 
At this point, you need to determine if it's a new
or previously used build server.  If new (or simply a new install 
on the same server), you'll need to create a virtual environment.

1. If `virtualenv` is not installed on your machine,
   [install it](http://virtualenv.readthedocs.org/en/latest/installation.html).  
   Afterwards, create an environment called "env":   
  ```
  virtualenv env
  ```
2. Next, activate the environment:
  ```
  source env/bin/activate
  ```

3. You should see your shell change with the environment activated.  Next
   install the the dependencies:
   
```
   pip install stomp.py pytz stompy
   
   pip install --upgrade -r PIP-DEPENDENCIES--packagebuilder.txt
   
   cd ../bioc-common-python
   
   pip install --upgrade -r PIP-DEPENDENCIES--bioc-common-python.txt
   
   python setup.py install
```
   
  **Note:** If there is trouble with a particular version of a dependency
   you can update the versions in these files. These versions were stable 
   and working on our systems. 
   
   **Note:** There are several system dependecies that may need to be 
   installed. Some common ones that have been needed if not already installed 
   are: libffi-dev, build-essential, libssl-dev, python-dev, openssl. These 
   generally would be installed with [sudo] apt-get install \<name\>
   

#### Configuration 

1.  Navigate back into the packagebuilder directory. Create a new directory
entitled `spb-properties` with a text file entitled `spb.properties`. Be mindful
of capitalization and punctuation. The `spb.properties` file should contain the
following: 
```
[Sensitive]
svn.user=
svn.pass=
tracker.user=
tracker.pass=
github.token=
```
    The values can be undefined. If you are deploying on a Bioconductor Build
    Node please grab this file from the private repository. 

2. You'll need to modify two configuration files. 

    i. Copy the provided `TEMPLATE.properties` to a unique properties file for
    your system `<host name>.properties`. Update all the values in this
    file as necessary. The `builders` value should match `<host name>`.

    ii. Secondly, change `bioconductor.properties` values. The `environment`
    variable should match  `<host name>` and update the BioC version
    accordingly
    
3. **NOTE:** For Bioconductor Nodes, you may need to copy over private/public key 
information from previous build nodes or on private GitHub.  

#### Start server
Kick off the server 
```
killall python
./run-build-server.sh
```

#### Automate

Crontab for pkgbuild on `<host name>`: 
```
@reboot /home/pkgbuild/packagebuilder/run-build-server.sh
00 04 * * * /home/pkgbuild/packagebuilder/run-cleanUpIssues.sh
```

# Windows Install: 

All steps should be performed as user `pkgbuild` unless otherwise noted.

#### Clone Repositories

```
git clone https://github.com/Bioconductor/packagebuilder.git
git clone git@github.com/Bioconductor/bioc-common-python.git
git clone git@github.com/Bioconductor/BBS.git
cd packagebuilder
```

#### Set Up Virtual Envirnment and Install Dependencies 
At this point, you need to determine if it's a new
or previously used build server.  If new (or simply a new install 
on the same server), you'll need to create a virtual environment.

1. If `virtualenv` is not installed on your machine,
   [install it](http://virtualenv.readthedocs.org/en/latest/installation.html).  
   Afterwards, create an environment called "env":   
```
    virtualenv env
```
2. Next, activate the environment:
```
    .\env\Scripts\activate
```

3. You should see your shell change with the environment activated.  Next
   install the the dependencies:
   
```
   pip install stomp.py pytz stompy
   
   pip install --upgrade -r PIP-DEPENDENCIES--packagebuilder.txt
   
   cd ../bioc-common-python
   
   pip install --upgrade -r PIP-DEPENDENCIES--bioc-common-python.txt
   
   python setup.py install
```
   
  **Note:** If there is trouble with a particular version of a dependency
   you can update the versions in these files. These versions were stable 
   and working on our systems. 

  **Note:** It may be necessary to log in as Administrator and run the 
  `pip install stomp.py pytz stompy` _without_ any virtual env activated
  

#### Configuration 

1.  Navigate back into the packagebuilder directory. Create a new directory
entitled `spb-properties` with a text file entitled `spb.properties`. Be mindful
of capitalization and punctuation. The `spb.properties` file should contain the
following: 
```
[Sensitive]
svn.user=
svn.pass=
tracker.user=
tracker.pass=
github.token=
```
    The values can be undefined. If you are deploying on a Bioconductor Build
    Node please grab this file from the private repository. 

2. You'll need to modify two configuration files. 

    i. Copy the provided `TEMPLATE.properties` to a unique properties file for
    your system `<host name>.properties`. Update all the values in this
    file as necessary. The `builders` value should match `<host name>`.

    ii. Secondly, change `bioconductor.properties` values. The `environment`
    variable should match  `<host name>` and update the BioC version
    accordingly
    
3. **NOTE:** For Bioconductor Nodes, you may need to copy over private/public key 
information from previous build nodes or on private GitHub.  
  
  **NOTE:** The single package builder utilizes directories shared with the 
  daily builder (biocbuild) mainly the same R. It may be necessary to have 
  an Administrator change permissions of these directories to allow read and 
  execute by pkgbuild 
  
  
#### Test server
You can test if the server will run by the following:
cd into the `~\pkgbuilder\packagebuilder`
```
.\env\Scripts\activate
killall python
python -m workers.server
```
This is just to test that the server will connect. You will want it to run 
through the task scheduler (see next section)

#### Automate

Set up a task scheduler to automate the launch of the server and clean up scripts. This will serve as a general guideline and will detail the steps used for the last setup. Keep in mind depending on your desired actions and system set up these may differ slightly. 

Log in as an Administrator account. 

Navigate the Serve Manager Dashboard, in the right top there is Tools, select Task Scheduler. Once this opens navigate down task scheduler -> Task Scheduler Library -> BBS.  On the right hand side select `create task`. We will now go through the details of the last setup in each of the tabs for a create task. 

1. General. Name your task. We generally have used spb\_server. Under Security Options, select Change User or Groups. In our case we will be running our tasks as the pkgbuild account. When set correctly this should show \<host name\>\\pkgbuild. This account will need to have `log on as batch job rights`. Make sure the "Run whether user is logged in or not" is selected and Change the "configure for"" to match the system. Our last deployment was `Windows Server 2012 R2` 
2. Triggers. Set the trigger to whatever is appropriate for your task. For the server task we will set the trigger to `At System Startup`. 
3. Actions. The following are the entries for the last set up of the spb_server task. Program/Script: `C:\Windows\System32\cmd.exe`.  Additional Arguments: `/C ".\env\Scripts\activate && python -m workers.server >> server.log 2>&1"` Start In: `C:\Users\pkgbuild\packagebuilder`.  Again these may differe depending on your locations and system setup. 
4. Conditions. All that should be selected are the following "Start task only if the computer is on AC power" and "Stop if computer switches to battery power".
5. Settings. All that should be selected are the following: "Allow task to be run on demand" and "If the running task does not end when requested force to stop"

We generally will create another task for spb\_package\_cleanUp. It has many of the same settings except the trigger is set to a daily time and the Action Additional Arguments: `/C ".\env\Scripts\activate && python workers\cleanUpIssues.py"`

If any additional tasks for the spb are added similar steps for the setup can be followed. 

# Adjust spb_history/staging.bioconductor.org

Log into staging.biocondcutor.org as `biocadmin`

1. Update staging.properties to include the new server[s] as a builder

2. Update viewhistory/static/css/2.7/report.css and
viewhistory/templates/base.html 
   **NOTE:** When entering server name, use all lowercase

3. Make sure the following are set in the crontab for `biocadmin@staging.bioconductor.org`:

```
@reboot /home/biocadmin/spb_history/run-archiver.sh
@reboot /home/biocadmin/spb_history/run-django.sh
@reboot /home/biocadmin/spb_history/run-track_build_completion.sh
```

3. Test
If the server is communicating correctly, on
'biocadmin@staging.bioconductor.org` run pinger.py. 

```
cd packagebuilder
. env/bin/activate
python pinger.py
```
There should be an entry for the new server provided it is running either 
interactively or automatically. 
  

# Other
Don't forget if these are replacing other build nodes or updating, go to the old
build nodes and turn off/kill the listeners and to comment out the crontab jobs
  