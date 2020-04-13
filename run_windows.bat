@call scripts/settings_windows.bat

@call conda activate %CONDA_ENV_NAME%

@set CONFIG=fomm/config/vox-adv-256.yaml

REM @set /P CAMID="Pick the webcam id you want to use (typically "0"): "

@set PYTHONPATH=%PYTHONPATH%;%CD%/fomm
@call python cam_fomm.py --config %CONFIG% --cam %CAMID% --relative --adapt_scale --no-pad --checkpoint vox-adv-cpk.pth.tar