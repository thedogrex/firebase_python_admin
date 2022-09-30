## Installation

Linux installation steps:

1. Install git

`sudo apt-get install git`

3. Update apt-get links

`sudo apt update`

upgrade system apps

`sudo apt upgrade`

4. Install build tools 
    `sudo apt-get install build-essential`

4. Install pyenv

- `curl https://pyenv.run | bash`

  (see instructions in console and add changes to files )

add this code to `~/.bash_profile` if it exists, otherwise `~/.profile` (for login shells)
and `~/.bashrc` files (for interactive shells) 

```bash
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
```

Add this code to ~/.bashrc

```bash
eval "$(pyenv virtualenv-init -)"
```

& Restart console to take effect (I am using putty connection )

Check that all works, try to update pyenv

```bash
pyenv update
```

5. Install python using pyenv

Because pyenv compiles python from sources we need to install some extra packages:
(also some blender packages included)

```bash
sudo apt-get update; sudo apt-get install --no-install-recommends make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev 

sudo apt-get install --no-install-recommends make libncurses5-dev tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

sudo apt-get install --no-install-recommends make wget curl llvm libxi6 libgconf-2-4 libglu1 xz-utils
```


Install 3.10.4 python version:

```bash
pyenv install 3.10.4
```

6. Set global python version:

   ```
   pyenv global 3.10.4
   ```

7. Update pip

 `python -m pip install --upgrade pip`



COPY GIT PROJECT AND CREATE VIRTUAL ENVIRONMENT FOR IT:

clone git repo into folder:

```
/home/ubuntu/firebase_admin
```

where ubuntu -> your user name (can be other)

navigate to cloned repository by a coomand:

```
cd firebase_admin
```

Create virtual env for future python modules

```
python -m venv venv
```

Activate virtual env:

```
source venv/bin/activate
```

8. install forked firebase-admin-python library for python:
   (have changed some token generation parameters there)

   ```
   pip install git+https://github.com/thedogrex/firebase-admin-python.git@master
   ```

9.Install flask

```
pip install flask
```



## Server bootstrap

#### Server bootstrap

Install all modules from Installation page. 

And after that setup server as described here.

### How it works:

##### [ Http(get,post) ] - [Nginx] - [GUnicorn] - [Python (Flask)]  

Nginx will work like a proxy to connect and process requests from on Flask python application. 
Gunicorn will work like a container for Flask applications (will create Flask instance automatically on each request)

### Setup

Update system:

1) `sudo apt update`

2) `sudo apt upgrade`

##### Install components:

​	`sudo apt install mc git curl wget rsync zip unzip`

##### Install nginx:

`sudo apt install nginx`

After nginx installation you can open page by server ip address (nginx will return html simple page). 
We will configure nginx to work as proxy server in future.

##### Setup gunicorn

`pip install gunicorn`



##### Setup Firewall

```
sudo apt install ufw
```

Turn on configurations of firewall:

```
sudo ufw allow 'OpenSSH'
sudo ufw allow 'Nginx Full'
```

And turn on Firewall:

```
sudo ufw enable
```



Need to restart ssh servie after:

```
sudo su
systemctl restart ssh
```

Disconnnect and reconnect after with putty ssh (or login/password)



#### Create Unit Services for GUnicorn:

Gunicorn service:

`/etc/systemd/system/gunicorn_my.service`

(`ubuntu` is user name -> type your user name in linux system instead of `ubuntu`)

change to correct user at paths too !!!

```
[Unit]
Description=Autorun gunicorn instance
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/firebase_admin
Environment="PATH=/home/ubuntu/firebase_admin/venv/bin"
ExecStart=/home/ubuntu/firebase_admin/venv/bin/gunicorn --workers 1 --timeout 180 --bind unix:gunicorn.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target

```


Note, that line:

```
ExecStart=/home/ubuntu/firebase_admin/venv/bin/gunicorn
```

must be the path of installed gunicorn component inside venv python virtual environment of the projecct



#### Add created services to autorun:

`sudo systemctl enable gunicorn_my`

`sudo systemctl enable nginx`



#### Setup nginx proxy:

remove `@default` file from `/etc/nginx/sites-enabled/` folder



create nginx conf file at path:
`/etc/nginx/conf.d/firebase_admin.conf`

file content:

*note that "ubuntu" here is your user name (I've created account with a name "ubuntu")

```
server {
	listen 80 default_server;
	listen [::]:80 default_server;
	
	location / {
		include proxy_params;
		proxy_pass http://unix:/home/ubuntu/firebase_admin/gunicorn.sock;
	}
}
```





Now you can reboot server machine and it should automatically run all services for blender render.
You can open ip address in browser /index page (it should display a message -> "Firebase admin server is running" )



Just open <u>http://[your-server-ip-address/index]</u> for check. You may see text message there.