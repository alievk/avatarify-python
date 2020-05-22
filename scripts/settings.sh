# [Linux] Virtual camera device
# Make sure this id is greater than maximum device id in the list `v4l2-ctl --list-devices`
# Don't set a big number, it's known that Zoom does not detect cameras with id like 99
CAMID_VIRT=9

# Conda environment name
CONDA_ENV_NAME=avatarify
