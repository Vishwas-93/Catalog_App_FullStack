# Catalog_App_FullStack
Flask | HTML | CSS | Bootstrap | SQLite | Jinja2 | Google Oauth2 API | Authorization | Flask Session |  API End Points


# Catalog Application

	*This application consists of multiple categories and each category has multiple items within them. This application is used to store each of them in the SQLite DB.

	*Perform DRUD operations on SQLite allowing the user to create, delete, edit and read from the DB.

	*This applications exposes data as an API endpoint that can be used by user or any other application.

	*Uses Google's OAuth to provide authentication and uses Flask session to provide authorization.

	*The user can only read the data from the DB without logging in. The user has to login to perform other operations like Create.
	
	*The user should be the owner of the item to be able to edit, delete the item.



# Installation Guide

Follow the instructions from Udacity's notes,

	* Download and install git bash to get a Linus style command prompt (On Windows)
	
	* Install Vagrant using the link (https://www.vagrantup.com/) 
	
	* Install VirtualBox using the link (https://www.virtualbox.org/)
	
	* cd to the vagrant directory. 

	* Launch the Vagrant VM using the command (vagrant up) on git bash/ Linux command prompt
	
	* Login using Vagrant ssh. 
	
	* 'cd /vagrant' This gives access to the shared directory between the host and Virtual Machine

	* install pycharm using the link (https://www.jetbrains.com/pycharm/download/#section=windows)

	* install Anaconda (https://conda.io/docs/user-guide/install/download.html)

	* Install any required package using: conda install (package-name) from the command prompt

	* Unzip the zipped document and paste inside the vagrant folder.

	* cd to the directory using Linux command prompt

	* run the views.py file in the unzipped downloaded folder using the command
		python views.py

	* Access and test your application by visiting http://localhost:8000


# Credits

	Few images have been taken from Google and may be prone to copyrights *

## Licence
