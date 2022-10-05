![](docs/mona.gif)

# Requirements

1- Nvidia RTX cards, recommend 8GB or more.

2- 6 core CPUs

3- 16GB RAM recommended (it may works on 8GB)

# We need to install a few dependencies on Windows first.

1- Install Git - [HERE](https://www.dropbox.com/s/lf5ammkeai68mpt/Git-2.38.0-64-bit.exe?dl=0)

2- Install Miniconda Python 3.7. - [HERE](https://www.dropbox.com/s/qogfyvcgpm8xjwb/Miniconda3-py37_4.12.0-Windows-x86_64.exe?dl=0)

3- Install CUDA for your GPU - [HERE](https://developer.nvidia.com/cuda-11-7-1-download-archive?target_os=Windows&target_arch=x86_64&target_version=11&target_type=exe_local)

# Installing the app and the model

Press the windows key and search for miniconda, open the app and you will have a terminal, then copy paste the commands below

```bash
git clone [https://github.com/technopremium/avatarify-python-youtube.git](https://github.com/technopremium/avatarify-python-youtube.git)
cd avatarify-python-youtube

```

# Important `Download the model before installing`

Download the model [HERE]([https://www.dropbox.com/s/vsokwc29rh1vqw3/vox-adv-cpk.pth.tar?dl=0](https://www.dropbox.com/s/vsokwc29rh1vqw3/vox-adv-cpk.pth.tar?dl=0)) 

<aside>
💡 Copy the file [vox-adv-cpk.pth.tar](https://www.dropbox.com/s/vsokwc29rh1vqw3/vox-adv-cpk.pth.tar?dl=0) to the avatarify-python-youtube folder and do not extract it.

</aside>

# Installing the app

Open the windows with miniconda and navigate to the avatrify-python-youtube folder if not there

```bash
cd avatarify-python-youtube
scripts\install_windows.bat
```

`This will take some time to install all the dependencies and files`

# Finally launching the app

```bash
run_windows.bat
```

<aside>
💡 Next time to start the app you just need to:

</aside>

1- Open miniconda terminal 

2- Navigate to the avatarify-python-youtube folder 

3- type on terminal run_windows.bat

# Enjoy

Original project - https://github.com/alievk/avatarify-python 

Thanks for this amazing project, I just make it easier for normal users to run on their machines.
