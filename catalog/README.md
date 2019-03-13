# Item-Catalog (Top Engineering Colleges)
This application provides a list of popular Engineering colleges in the states within india as well as provide a user registration(google)and authentication system. Registered users will have the ability to post, edit and delete their own colleges in different states.It utilizes Flask, SQL Alchemy, JQUERY, CSS, Java Script, and OAUTH 2 to create an Item catalog website.

# Files Included
* database.py
* clgdata_entry.py
* main.py
* static folder
* templates folder
* client_secrets.json

## Setup and run the project
### Prerequisites
* Python 2.7
* Vagrant
* VirtualBox

# Installation
There are some dependancies and a few instructions on how to run the application.
Seperate instructions are provided to get GConnect working also.

## Dependencies
- [Vagrant](https://www.vagrantup.com/)
- [Udacity Vagrantfile](https://github.com/udacity/fullstack-nanodegree-vm)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)



## How to Install
1. Install Vagrant & VirtualBox
2. Clone the Udacity Vagrantfile
3. Go to Vagrant directory and either clone this repo or download and place zip here
3. Launch the Vagrant VM (`vagrant up`)
4. Log into Vagrant VM (`vagrant ssh`)
5. Navigate to `cd /vagrant` as instructed in terminal
6. The app imports requests which is not on this vm. Run pip install requests

Or you can simply Install the dependency libraries (Flask, sqlalchemy, requests,psycopg2 and oauth2client) by running 
`pip install -r requirements.txt`

7. Setup application database `python /colleges/database.py`
8. *Insert sample data `python /colleges/clgdata_entry.py`
9. Run application using `python /colleges/main.py`
10. Access the application locally using http://localhost:9876

*Optional step(s)

## Using Google Login
To get the Google login working there are a few additional steps:

1. Go to [Google Dev Console](https://console.developers.google.com)
2. Sign up or Login if prompted
3. Go to Credentials
4. Select Create Crendentials > OAuth Client ID
5. Select Web application
6. Enter name 'colleges'
7. Authorized JavaScript origins = 'http://localhost:9876'
8. Authorized redirect URIs = 'http://localhost:9876/login' && 'http://localhost:9876/gconnect'
9. Select Create
10. Copy the Client ID and paste it into the `data-clientid` in login.html
11. On the Dev Console Select Download JSON
12. Rename JSON file to client_secrets.json
13. Place JSON file in colleges directory that you cloned from here
14. Run application using `python /colleges/main.py`
10. Open the browser and go to http://localhost:9876


# JSON Endpoints
The following are open to the public:

colleges Catalog JSON: `/colleges/JSON`
    - Displays the whole colleges  catalog. college Categories and all models.

college Categories JSON: `/colleges/collegeCategories/JSON`
    - Displays all college categories(states)
All colleges: `/colleges/college/JSON`
	- Displays all colleges

college Edition JSON: `/colleges/<path:college_name>/college/JSON`
    - Displays colleges for a specific college category

college Category Edition JSON: `/colleges/<path:college_name>/<path:edition_name>/JSON`
    - Displays a specific college category .



