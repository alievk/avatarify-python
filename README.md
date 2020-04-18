![](docs/mona.gif)


[<img src="https://img.shields.io/badge/slack-join-brightgreen?style=flat&logo=slack">](https://join.slack.com/t/avatarify/shared_invite/zt-dyoqy8tc-~4U2ObQ6WoxuwSaWKKVOgg)

:arrow_forward: [Demo](https://youtu.be/Q7LFDT-FRzs) 

:arrow_forward: [AI-generated Elon Musk](https://youtu.be/lONuXGNqLO0)

# Avatarify

Avatars for Skype and Zoom. Democratized.

**Disclaimer**: This project is unrelated to Samsung AI Center.

## News
- **17 April 2020.** Created Slack community. Please join via [invitation link](https://join.slack.com/t/avatarify/shared_invite/zt-dyoqy8tc-~4U2ObQ6WoxuwSaWKKVOgg).
- **15 April 2020.** Added [StyleGAN-generated](https://www.thispersondoesnotexist.com) avatars. Just press `Q` and now you drive a person that never existed. Every time you push the button – new avatar is sampled.
- **13 April 2020.** Added Windows support (kudos to [9of9](https://github.com/9of9)).

## Table of Contents
- [Avatarify](#avatarify)
  - [News](#news)
  - [Table of Contents](#table-of-contents)
  - [Requirements](#requirements)
  - [Install](#install)
      - [Download network weights](#download-network-weights)
      - [Linux](#linux)
      - [Mac](#mac)
      - [Windows](#windows)
  - [Setup avatars](#setup-avatars)
  - [Run](#run)
      - [Linux](#linux-1)
      - [Mac](#mac-1)
      - [Windows](#windows-1)
  - [Controls](#controls)
  - [Driving your avatar](#driving-your-avatar)
  - [Configure video meeting app](#configure-video-meeting-app)
    - [Skype](#skype)
    - [Zoom](#zoom)
    - [Slack](#slack)
  - [Contribution](#contribution)
  - [Troubleshooting](#troubleshooting)
  - [Credits](#credits)

## Requirements

To run Avatarify smoothly you need a CUDA-enabled (NVIDIA) video card. Otherwise it will fallback to the central processor and run very slowly. These are performance metrics for some hardware:

- GeForce GTX 1080 Ti: **33 fps**
- GeForce GTX 1070: **15 fps**
- Mac OSX (MacBook Pro 2018; no GPU): **very slow** **~1 fps**

Of course, you also need a webcam!

<!-- * [conda Python 3.7](https://docs.conda.io/en/latest/miniconda.html)
* [CUDA](https://developer.nvidia.com/cuda-downloads) -->

## Install

#### Download network weights
Download model's weights from [Yandex.Disk](https://yadi.sk/d/lEw8uRm140L_eQ/vox-adv-cpk.pth.tar) or [Google Drive](https://drive.google.com/file/d/1L8P-hpBhZi8Q_1vP2KlQ4N6dvlzpYBvZ/view) [716 MB, md5sum `46b26eabacbcf1533ac66dc5cf234c5e`]

#### Linux
Linux uses `v4l2loopback` to create virtual camera.

1. Install [CUDA](https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64).
2. Download [Miniconda Python 3.7](https://docs.conda.io/en/latest/miniconda.html#linux-installers) and install using command:
```bash
bash Miniconda3-latest-Linux-x86_64.sh
```
3. Clone `avatarify` and install its dependencies (sudo privelege is required):
```bash
git clone https://github.com/alievk/avatarify.git
cd avatarify
bash scripts/install.sh
```
4. [Download network weights](#download-network-weights) and place `vox-adv-cpk.pth.tar` file in the `avatarify` directory (don't unpack it).

#### Mac
*(!) Note*: we found out that in versions after [v4.6.8 (March 23, 2020)](https://zoom.us/client/4.6.19178.0323/ZoomInstaller.pkg) Zoom disabled support for virtual cameras on Mac. To use Avatarify in Zoom you can choose from 2 options:
- Install [Zoom v4.6.8](https://zoom.us/client/4.6.19178.0323/ZoomInstaller.pkg) which is the last version that supports virtual cameras
- Use latest version of Zoom, but disable library validation:
```bash
codesign --remove-signature /Applications/zoom.us.app
```

For Mac it's quite difficult to create a virtual camera, so we'll use [CamTwist](http://camtwiststudio.com) app.

1. Install [Miniconda Python 3.7](https://docs.conda.io/en/latest/miniconda.html#macosx-installers).
2. Clone `avatarify` and install its dependencies:
```bash
git clone https://github.com/alievk/avatarify.git
cd avatarify
bash scripts/install_mac.sh
```
3. [Download network weights](#download-network-weights) and place `vox-adv-cpk.pth.tar` file in the `avatarify` directory (don't unpack it).
4. Download and install [CamTwist](http://camtwiststudio.com) from [here](http://camtwiststudio.com/download). It's easy.

#### Windows

*Video tutorial is coming!*

This guide is tested for Windows 10.

1. Install [CUDA](https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64&target_version=10&target_type=exenetwork).
2. Install [Miniconda Python 3.7](https://docs.conda.io/en/latest/miniconda.html#windows-installers).
3. Install [Git](https://git-scm.com/download/win).
4. Press Windows button and type "miniconda". Run suggested Anaconda Prompt.
5. Download and install Avatarify (please copy-paste these commands and don't change them):
```bash
git clone https://github.com/alievk/avatarify.git
cd avatarify
scripts\install_windows.bat
```
6. [Download network weights](#download-network-weights) and place `vox-adv-cpk.pth.tar` file in the `avatarify` directory (don't unpack it).
7. Run `run_windows.bat`. If installation was successful, two windows "cam" and "avatarify" will appear. Leave these windows open for the next installation steps. If there are multiple cameras (including virtual ones) in the system, you may need to select the correct one. Open `scripts/settings_windows.bat` and edit `CAMID` variable. `CAMID` is an index number of camera like 0, 1, 2, ...
8. Install [OBS Studio](https://obsproject.com/) for capturing Avatarify output.
9. Install [VirtualCam plugin](https://obsproject.com/forum/resources/obs-virtualcam.539/). Choose `Install and register only 1 virtual camera`.
10. Run OBS Studio.
11. In the Sources section, press on Add button ("+" sign), select Windows Capture and press OK. In the appeared window, choose "[python.exe]: avatarify" in Window drop-down menu and press OK. Then select Edit -> Transform -> Fit to screen.
12. In OBS Studio, go to Tools -> VirtualCam. Check AutoStart, set Buffered Frames to 0 and press Start.
13. Now `OSB-Camera` camera should be available in Zoom (or other videoconferencing software).

The steps 11-12 are required only once during setup.

## Setup avatars
Avatarify comes with a standard set of avatars of famous people, but you can extend this set simply copying your avatars into `avatars` folder.

Follow these advices for better visual quality:
* Make square crop of your avatar picture.
* Crop avatar's face so that it's not too close not too far. Use standard avarars as reference.
* Prefer pictures with uniform background. It will diminish visual artifacts.

## Run
Your web cam must be plugged-in.

**Note:** run Skype or Zoom only after Avatarify is started.

#### Linux
It is supposed that there is only one web cam connected to the computer at `/dev/video0`. The run script will create virtual camera `/dev/video9`. You can change these settings in `scripts/settings.sh`.

You can use command `v4l2-ctl --list-devices` to list all devices in your system. For example, if the web camera is `/dev/video1` then the device id is 1. 

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
4. In the `Settings` section choose `Confine to Application Window` and select `python (avatarify)` from the drop-down menu.

#### Windows

If there are multiple cameras (including virtual ones) in your system, you may need to select the correct one in `scripts/settings_windows.bat`. Open this file and edit `CAMID` variable. `CAMID` is an index number of camera like 0, 1, 2, ...

1. In Anaconda Prompt:
```
cd C:\path\to\avatarify
run_windows.bat
```
2. Run OBS Studio. It should automaitcally start streaming video from Avatarify to `OBS-Camera`.

**Note:** To reduce video latency, in OBS Studio right click on the preview window and uncheck Enable Preview.

## Controls


Keys | Controls
--- | ---
1-9 | These will immediately switch between the first 9 avatars.
Q | Turns on StyleGAN-generated avatar. Every time you push the button – new avatar is sampled.
0 | Toggles avatar display on and off.
A/D | Previous/next avatar in folder.
W/S | Zoom camera in/out.
Z/C | Adjust avatar target overlay opacity.
X | Reset reference frame.
F | Toggle reference frame search mode.
R | Mirror reference window.
T | Mirror output window.
ESC | Quit

## Driving your avatar

It is recommended to use the avatar overlay and the zoom in/out function to align your face in the preview window as closely as possible in proportion and position to the target avatar. When you have aligned, hit 'X' to use this frame as reference to drive the rest of the animation.

Alternatively, you can hit 'F' for the software to attempt to find a better reference frame itself. This will slow down the framerate, but while this is happening, you can keep moving your head around: the preview window will flash green when it finds your facial pose is a closer match to the avatar than the one it is currently using. You will see two numbers displayed as well: the first number is how closely you are currently aligned to the avatar, and the second number is how closely the reference frame is aligned.

You want to get the first number as small as possible - around 10 is usually a good alignment. When you are done, press 'F' again to exit reference frame search mode.

You don't need to be exact, and some other configurations can yield better results still, but it's usually a good starting point.

## Configure video meeting app

### Skype

Go to Settings -> Audio & Video, choose `avatarify` (Linux), `CamTwist` (Mac) or `OBS-Camera` (Windows) camera.

<img src=docs/skype.jpg width=600>

### Zoom

Go to Settings -> Video and choose `avatarify` (Linux), `CamTwist` (Mac) or `OBS-Camera` (Windows) from Camera drop-down menu.

<img src=docs/zoom.jpg width=600>

### Slack

Make a call, allow browser using cameras, click on Settings icon, choose `avatarify` (Linux), `CamTwist` (Mac) or `OBS-Camera` (Windows) in Video settings drop-down menu.

<img src=docs/slack.jpg width=600>


## Contribution

Our goal is to democratize deepfake avatars. To make the technology even more accessible, we have to tackle two major problems:

1. Add support for more platforms (Linux and Mac are already supported).
2. Optimize neural network run-time. Running network real-time on CPU is of high priority.

Please make pull requests if you have any improvements or bug-fixes.


## Troubleshooting

* *Zoom/Skype doesn't see `avatarify` camera*. Restart Zoom/Skype and try again.
* *Avatar image is frozen*: In Zoom, try Stop and Start Video.
* *`bash run_mac.sh` crashes with "Cannot open camera"*: Try to change CAMID in `run_mac.sh` from `0` to `1`, `2`, ...
* `pipe:0: Invalid data found when processing input`: Make sure `CAMID` in `scripts/settings.sh` is correct. Use `v4l2-ctl --list-devices` to query available devices.
* `ASSERT: "false" in file qasciikey.cpp, line 501`. If you have several keyboard layouts, switch to English layout.
* `No such file or directory: 'vox-adv-cpk.pth.tar'`. Please follow instructions [Download network weights](#download-network-weights)


## Credits

- Avatrify uses [First Order Motion Model](https://github.com/AliaksandrSiarohin/first-order-model) for generating avatars.
