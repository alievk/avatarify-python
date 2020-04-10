![](docs/mona.gif)

# Avatarify

Avatars for Skype and Zoom. Democratized. Specifically for Windows.

## Requirements

* [conda](https://docs.conda.io/en/latest/miniconda.html)
* [CUDA](https://developer.nvidia.com/cuda-downloads)

## Performance:
- Windows (with 1080 Ti GPU): **33 fps**

## Install

#### Download
1. Download model's weights from [Google Drive](https://drive.google.com/file/d/1L8P-hpBhZi8Q_1vP2KlQ4N6dvlzpYBvZ/view) [716 MB]
2. Place `vox-adv-cpk.pth.tar` file in the root directory

#### Windows

1. Setup `avatarify` conda environment with all required dependencies. Open your miniconda command prompt, navigate to the avatarify-windows folder and run:
```install.bat```
2. Now execute ```run.bat``` - you should now see the application running, and two windows will appear, if everything is working correctly.
3. To output to webcam, download and install [OBS](http://obsproject.com)
4. Download and install the latest Windows release of [OBS-VirtualCam](https://github.com/CatxFish/obs-virtual-cam/releases)
5. Reboot.
6. You are now able to use OBS to capture the output window of Avatarify, and output your result to a virtual webcam.

## Setup avatars
Copy your avatars into `avatars` folder. Crop pictures to make them square. Prefer pictures with uniform background.

## Run
Your web cam must be plugged-in. You can choose your camera when running ```run.bat```

## Tips

Your face should fit in the red rectagle: it should not fit perfectly, but don't get too close/far. After that, press any number from 0 to 9 on your keyboard and one of the avatars from `avatars` directory will appear.

You can also use the A and D keys to scroll through your avatars folder, if you have more than one avatar available.

Run Skype or Zoom only when Avatarify is running.

### Skype

Go to Settings -> Audio & Video, choose `OBSCam` camera.

### Zoom

Go to Settings -> Video and choose `OBSCam` from Camera drop-down menu.

### Slack

Make a call, allow browser using cameras, click on Settings icon, choose `avatarify` in Video settings drop-down menu.

![Slack](docs/slack.jpg)


## Contribution

Forked from [Avatarify](https://github.com/alievk/avatarify) and adapted for Windows.

## Credits

- Avatrify uses [First Order Motion Model](https://github.com/AliaksandrSiarohin/first-order-model) for generating avatars.
