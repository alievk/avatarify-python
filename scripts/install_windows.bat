@echo off

REM Check prerequisites
call conda --version >nul 2>&1 && ( echo conda found ) || ( echo conda not found. Please refer to the README and install Miniconda. && exit /B 1)
REM call git --version >nul 2>&1 && ( echo git found ) || ( echo git not found. Please refer to the README and install Git. && exit /B 1)

call scripts/settings_windows.bat

call conda create -y -n %CONDA_ENV_NAME% python=3.7
call conda activate %CONDA_ENV_NAME%

call conda install -y numpy==1.19.0 scikit-image python-blosc==1.7.0 -c conda-forge
call conda install -y pytorch==1.7.1 torchvision cudatoolkit=11.0 -c pytorch
call conda install -y -c anaconda git

REM ###FOMM###
call rmdir fomm /s /q
call git clone https://github.com/alievk/first-order-model.git fomm

call pip install -r requirements.txt --use-feature=2020-resolver
