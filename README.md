![](docs/mona.gif)

:arrow_forward: [Demo](https://youtu.be/Q7LFDT-FRzs) 

:arrow_forward: [AI-generated Elon Musk](https://youtu.be/lONuXGNqLO0)

# Avatarify

Avatars for Skype and Zoom. Democratized.

**Disclaimer**: This project is unrelated to Samsung AI Center.

## News

* 13 April 2020. Added Windows support (kudos to [9of9](https://github.com/9of9)) 

## Requirements

* [conda](https://docs.conda.io/en/latest/miniconda.html)
* [CUDA](https://developer.nvidia.com/cuda-downloads)

## Performance:
- 1080 Ti GPU: **33 fps**
- 1070 GPU: **15 fps**
- Mac OSX (MacBook Pro 2018; no GPU): **very slow** **~1 fps**

## Install

#### Download network weights
1. Download model's weights from [Google Drive](https://drive.google.com/file/d/1L8P-hpBhZi8Q_1vP2KlQ4N6dvlzpYBvZ/view) or [Yandex.Disk](https://yadi.sk/d/lEw8uRm140L_eQ/vox-adv-cpk.pth.tar) [716 MB]
2. Place `vox-adv-cpk.pth.tar` file in the `avatarify` root directory

#### Linux
Linux uses `v4l2loopback` to create virtual camera.

Install `avatarify` dependencies (sudo privelege is required):

```bash
bash scripts/install.sh
```

#### Mac
*(!) Note*: we found out that in versions after [v4.6.8 (March 23, 2020)](https://zoom.us/client/4.6.19178.0323/ZoomInstaller.pkg) Zoom disabled support for virtual cameras on both Mac and Windows. Please, install [Zoom v4.6.8](https://zoom.us/client/4.6.19178.0323/ZoomInstaller.pkg) which is the last version that supports virtual cameras.

For Mac it's quite difficult to create a virtual camera, so we'll use [CamTwist](http://camtwiststudio.com) app:

1. Download and install [CamTwist](http://camtwiststudio.com) from [here](http://camtwiststudio.com/download). It's easy.
2. Setup `avatarify` conda environment with all required dependencies:
```bash
source scripts/install_mac.sh
```

#### Windows

This guide is tested for Windows 10.

1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for Windows.
2. Press Windows button and type "miniconda". Run suggested Anaconda Prompt.
3. In the prompt, run the following commands:
```bash
git clone https://github.com/alievk/avatarify.git
cd avatarify
scripts\install_windows.bat
```
4. Run `run_windows.bat`. If installation was successful, two windows "cam" and "avatarify" will appear. Leave these windows open for the next installation steps. If there are multiple cameras (including virtual ones) in the system, you may need to select the correct one in `scripts/settings_windows.bat` `CAMID` variable. `CAMID` is an index number of camera like 0, 1, 2, ...
5. Install [OBS Studio](https://obsproject.com/) for capturing Avatarify output.
6. Install [VirtualCam plugin](https://obsproject.com/forum/resources/obs-virtualcam.539/). Choose `Install and register only 1 virtual camera`.
7. Run OBS Studio.
8. In the Sources section, press on Add button ("+" sign), select Windows Capture and press OK. In the appeared window, choose "[python.exe]: avatarify" in Window drop-down menu and press OK. Then select Edit -> Transform -> Fit to screen.
9. In OBS Studio, go to Tools -> VirtualCam. Check AutoStart, set Buffered Frames to 0 and press Start.
10. Now `OSB-Camera` camera should be available in Zoom (or other videoconferencing software).

The steps 8-9 are required only once during setup.

## Setup avatars
Copy your avatars into `avatars` folder. Crop pictures to make them square. Prefer pictures with uniform background.

## Run
Your web cam must be plugged-in. You can choose your camera by changing `CAMID` in `scripts/settings.sh` script.

Run Skype or Zoom only when Avatarify is started.

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

If there are multiple cameras (including virtual ones) in the system, you may need to select the correct one in `scripts/settings_windows.bat` `CAMID` variable. `CAMID` is an index number of camera like 0, 1, 2, ...

1. In Anaconda Prompt:
```
cd C:\path\to\avatarify
run_windows.bat
```
2. Run OBS Studio. It should automaitcally start streaming video from Avatarify to `OBS-Camera`.

To reduce video latency, in OBS Studio right click on the preview window and uncheck Enable Preview.

## Controls


Keys | Controls
--- | ---
1-9 | These will immediately switch between the first 9 avatars.
0 | Toggles avatar display on and off.
A/D | Previous/next avatar in folder.
W/S | Zoom camera in/out.
Z/C | Adjust avatar target overlay opacity.
X | Reset reference frame.
F | Toggle reference frame search mode.
R | Mirror reference window.
T | Mirror output window.
ESC | Quit

## Tips

It is recommended to use the avatar overlay and the zoom in/out function to align your face in the preview window as closely as possible in proportion and position to the target avatar. When you have aligned, hit 'X' to use this frame as reference to drive the rest of the animation.

Alternatively, you can hit 'F' for the software to attempt to find a better reference frame itself. This will slow down the framerate, but while this is happening, you can keep moving your head around: the preview window will flash green when it finds your facial pose is a closer match to the avatar than the one it is currently using. You will see two numbers displayed as well: the first number is how closely you are currently aligned to the avatar, and the second number is how closely the reference frame is aligned.

You want to get the first number as small as possible - around 10 is usually a good alignment. When you are done, press 'F' again to exit reference frame search mode.

You don't need to be exact, and some other configurations can yield better results still, but it's usually a good starting point.

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
