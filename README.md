![](docs/mona.gif)

# Avatarify

Avatars for Skype and Zoom. Democratized.

## Requirements

* conda

This app is tested only on GPU and Linux (Ubuntu 18.04).

## Install

#### Linux
It is supposed that there is only one web cam connected to the computer and it's in `/dev/video0`. Installation process will create a virtual camera `/dev/video1`, so this device must be reserved.

```bash
source scripts/install.sh
bash scripts/download_data.sh
```

#### Mac
For Mac it's quite difficult to create a virtual camera, so we'll use [CamTwist](http://camtwiststudio.com) app:

1. Download and install [CamTwist](http://camtwiststudio.com) from [here](http://camtwiststudio.com/download). It's easy.
2. Setup `avatarify` conda environment with all required dependencies:
```bash
source scripts/install_mac.sh
```
3. Download models' weights:
```bash
bash scripts/download_data.sh
```

## Setup avatars
Copy your avatars into `avatars` folder. Crop pictures to make them square. Prefer pictures with uniform background.

## Run
Your web cam must be plugged-in. You can choose your camera by changing `CAMID` in `run*.sh` script.

#### Linux
Run:
```bash
bash run.sh
```

#### Mac
1. Run:
```bash
bash run_mac.sh
```
2. Go to [CamTwist](http://camtwiststudio.com).
3. Choose `Desktop+` and press `Select`.
4. In the `Settings` sction choose `Confine to Application Window` and select `python (avatarify)` from the drop-down menu.


## Tips

Your face should fit in the red rectagle: it should not fit perfectly, but don't get too close/far. After that, press any number from 0 to 9 on your keyboard and one of the avatars from `avatars` directory will appear.

Run Skype or Zoom only when Avatarify is running.

### Skype

Go to Settings -> Audio & Video, choose `avatarify` or `CamTwist` camera.

![Skype](docs/skype.jpg)

### Zoom

Go to Settings -> Video and choose `avatarify` or `CamTwist` from Camera drop-down menu.

![Zoom](docs/zoom.jpg)


## Contribution

Our goal is to democratize deepfake avatars. To make the technology even more accessible, we have to tackle two major problems:

1. Add support for more platforms (Linux and Mac are already supported).
2. Optimize neural network run-time. Running network real-time on CPU is of high priority.

Please make pull requests if you have any improvements or bug-fixes.


## Troubleshooting

* *Zoom/Skype doesn't see `avatarify` camera*. Restart Zoom/Skype and try again.
* *Avatar image is frozen*: In Zoom, try Stop and Start Video.
