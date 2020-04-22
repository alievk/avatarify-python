call scripts/settings_windows.bat

call conda create -y -n %CONDA_ENV_NAME% python=3.7
call conda activate %CONDA_ENV_NAME%

call conda install -y pytorch==1.0.0 torchvision==0.2.1 cuda100 -c pytorch

REM ###FOMM###
call git clone https://github.com/alievk/first-order-model.git fomm

call pip install -r requirements.txt
