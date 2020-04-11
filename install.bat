set env_name=avatarify

call conda create -y -n %env_name% python=3.8
call conda activate %env_name%

call conda install pytorch torchvision cudatoolkit=10.1 -c pytorch
call conda install -c 1adrianb face_alignment

REM ###FOMM###
call git clone https://github.com/alievk/first-order-model.git fomm
call pip install -r fomm/requirements.txt
