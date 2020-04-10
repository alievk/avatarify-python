# Web-camera device id
# Call `v4l2-ctl --list-devices` and find your web-camera device, e.g. /dev/videoX, where X is camera id
export CAMID=0

# Virtual camera device (normally you don't want to change this)
# Make sure this id is greater than maximum device id in the list `v4l2-ctl --list-devices`
# Don't set a big number, it's known that Zoom does not detect cameras with id like 99
export CAMID_VIRT=9