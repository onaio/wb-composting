WBComposting README
==================

Run with [Vagrant](http://www.vagrantup.com/)
-------------------

### Installing

1. Download Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

2. Download Install [Vagrant](http://www.vagrantup.com/downloads.html)

3. Install Ansible, preferably [from source](http://docs.ansible.com/intro_installation.html#running-from-source)

    ```
    cd ~/
    git clone git://github.com/ansible/ansible.git
    cd ./ansible
    source ./hacking/env-setup
    ```

    If you don’t have pip installed in your version of Python, install pip (No harm running it if its already installed):

    ```
    sudo easy_install pip
    ```

    Install Ansible's requirements

    ```
    sudo pip install paramiko PyYAML jinja2 httplib2
    ```

4. Change back into the project's directory

    ```
    cd /path/to/this/project
    ```

5. Clone the Ona playbooks repo (into a different directory)
    ```
    git clone git@github.com:onaio/playbooks.git ~/playbooks
    ```

6. Make a symbolic link to the playbooks directory
    ```
    ln -s ~/playbooks ansible
    ```

7. Bring up the virtual machine with Vagrant
    ```
    vagrant up
    ```

    NOTE: This will keep the virtual machine running until you halt it via `vagrant halt`

8. Provision using ansible
    ```
    vagrant provision
    ```

    NOTE: To update to the latest version at any time, run the provision command again.

### Running

1. ssh into the virtual machine
    ```
    vagrant ssh
    ```

2. Change into the project's directory
    ```
    cd /vagrant
    ```

3. Activate the virtual environment
    ```
    source ~/.virtualenvs/composting/bin/activate
    ```

4. Run the server
    ```
    pserve development --reload
    ```

    Load the app in your browser at http://192.168.33.15:6543/

    You can now make edits from your host (read OSX) and have them reflected when you refresh the browser.

