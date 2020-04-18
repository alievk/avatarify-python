call scripts/settings_windows.bat

call conda create -y -n %CONDA_ENV_NAME% python=3.8
call conda activate %CONDA_ENV_NAME%

call conda install -y pytorch torchvision cudatoolkit=10.1 -c pytorch
call conda install -y -c 1adrianb face_alignment

REM ###FOMM###
call git submodule update --init
call pip install -r fomm/requirements.txt
call pip install requests
