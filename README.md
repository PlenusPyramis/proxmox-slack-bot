# proxmox-slack-bot

Create KVM Virtual Machines on Proxmox, the easy way.

Not much works works here yet...

## Setup dev environment

Setup fully editable stack for:
 
  * proxmox-slack-bot
  * fastapi
  * starlette
  * pydantic
  
```
VENDOR_ROOT=$HOME/git/vendor
PROJECT_ROOT=$VENDOR_ROOT/plenuspyramis/proxmox-slack-bot
PROJECT_ENV=$PROJECT_ROOT/env

# Clone dependencies to seperate vendor dirs:
git clone https://github.com/PlenusPyramis/proxmox-slack-bot.git \
    $PROJECT_ROOT
git clone https://github.com/tiangolo/fastapi.git \
    $VENDOR_ROOT/tiangolo/fastapi
git clone https://github.com/encode/starlette.git \
    $VENDOR_ROOT/encode/starlette
git clone https://github.com/samuelcolvin/pydantic.git \
    $VENDOR_ROOT/samuelcolvin/pydantic

# Create virtualenv in main project dir:
virtualenv $PROJECT_ENV --prompt "(proxmox-slack-bot) "

# Activate the virutalenv:
source $PROJECT_ENV/bin/activate

# Upgrade pip inside the virtualenv:
# (You must use pip >= 19.1.1 in order to install an editable fastapi)
pip install --upgrade pip


# Install all dependencies in place:
pip install -e $VENDOR_ROOT/samuelcolvin/pydantic/
pip install -e $VENDOR_ROOT/encode/starlette

# Fastapi cannot be pip installed in place :(
# as a workaround create a .pth file in the virtualenv:
echo $VENDOR_ROOT/tiangolo/fastapi > $PROJECT_ENV/lib/python3.7/site-packages/fastapi.pth

# Install additional fastapi dependencies manually:
pip install -r $PROJECT_ROOT/dev-requirements.txt

# start a fastapi demo app to test the setup:
cd $PROJECT_ROOT/demo
uvicorn main:app --reload
```
