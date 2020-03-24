# Web Deployment

In order to use the UI of MATRIX, you will need to install and deploy it on a machine (local/cloud).  
The installation instructions are are an addition to the MATRIX installation instructions.

### Installation
To install Angular 9:
1. install Nodejs and npm: `curl -sL https://deb.nodesource.com/setup_12.x | sudo bash - && 
sudo apt-get install -y nodejs`
2. Install the Angular CLI: `npm install -g @angular/cli@9`
3. Install the required JS packages: `cd WebApp/frontend && npm install`

#### Mongodb

Matrix uses mongodb. In order to use MATRIX you must install and configure Mongodb.
To install Mongodb: `sudo apt install mongodb`
To configure the database to support authentication use this SO [answer](https://stackoverflow.com/a/55839446/4193208).
Please name the database `BIU`. If you cwant to create the database in a different name, please change this 
[line](https://github.com/cryptobiu/MATRIX/blob/3298d08bcd4c4a2260f87d270d41fe2d898a3462/WebApp/app.py#L28).


### Deployment

To use the UI, you will need to deploy two web services. The deployment is done on
[Nginx](https://www.nginx.com/) server.
To install Nginx: `sudo apt install nginx`
To deploy the Angular service:

1. Build the Angular project for production: `cd WebApp/frontend && ng build -- prod` 
2. Create directory `mkdir -p /usr/share/nginx/html/matrix`
3. Copy `WebApp/frontend/dist/frontend` to `/usr/share/nginx/html/matrix`
4. Copy `WebApp/matrix` to `/etc/nginx/sites-available/`
5. Restart Nginx service: `sudo systemctl restart nginx`

To deploy the backend service use `gunicorn`. To install it run: `pip3 install gunicorn --user`.
After the installation finished run inside MATRIX root directory:
`gunicorn  -m 007 app:app --chdir WebApp -b 0.0.0.0:5000`
