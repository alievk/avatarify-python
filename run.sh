#!/usr/bin/env bash

# set -x

ENABLE_CONDA=1
ENABLE_VCAM=1
KILL_PS=1
USE_DOCKER=0
IS_WORKER=0
IS_CLIENT=0
DOCKER_IS_LOCAL_CLIENT=0
DOCKER_NO_GPU=0

FOMM_CONFIG=fomm/config/vox-adv-256.yaml
FOMM_CKPT=vox-adv-cpk.pth.tar

ARGS=""
DOCKER_ARGS=""

while (( "$#" )); do
    case "$1" in
        --no-conda)
            ENABLE_CONDA=0
            shift
            ;;
        --no-vcam)
            ENABLE_VCAM=0
            ARGS="$ARGS --no-stream"
            shift
            ;;
        --keep-ps)
            KILL_PS=0
            shift
            ;;
        --docker)
            USE_DOCKER=1
            shift
            ;;
        --no-gpus)
            DOCKER_NO_GPU=1
            shift
            ;;
        --is-worker)
            IS_WORKER=1
            ARGS="$ARGS $1"
            DOCKER_ARGS="$DOCKER_ARGS -p 5557:5557 -p 5558:5558"
            shift
            ;;
        --is-client)
            IS_CLIENT=1
            ARGS="$ARGS $1"
            shift
            ;;
        --is-local-client)
            IS_CLIENT=1
            DOCKER_IS_LOCAL_CLIENT=1
            ARGS="$ARGS --is-client"
            shift
            ;;
        *|-*|--*)
            ARGS="$ARGS $1"
            shift
            ;;
    esac
done

eval set -- "$ARGS"



if [[ $USE_DOCKER == 0 ]]; then
    
    if [[ $KILL_PS == 1 ]]; then
        kill -9 $(ps aux | grep 'afy/cam_fomm.py' | awk '{print $2}') 2> /dev/null
    fi
    
    source scripts/settings.sh
    
    if [[ $ENABLE_VCAM == 1 ]]; then
        bash scripts/create_virtual_camera.sh
    fi
    
    if [[ $ENABLE_CONDA == 1 ]]; then
        source $(conda info --base)/etc/profile.d/conda.sh
        conda activate $CONDA_ENV_NAME
    fi
    
    export PYTHONPATH=$PYTHONPATH:$(pwd):$(pwd)/fomm
    
    python afy/cam_fomm.py \
        --config $FOMM_CONFIG \
        --checkpoint $FOMM_CKPT \
        --virt-cam $CAMID_VIRT \
        --relative \
        --adapt_scale \
        $@
else

    source scripts/settings.sh
    
    if [[ $ENABLE_VCAM == 1 ]]; then
        bash scripts/create_virtual_camera.sh
    fi
    
    if [[ $DOCKER_NO_GPU == 0 ]]; then
        DOCKER_ARGS="$DOCKER_ARGS --gpus all"
    fi

    if [[ $DOCKER_IS_LOCAL_CLIENT == 1 ]]; then
        DOCKER_ARGS="$DOCKER_ARGS --network=host"
    elif [[ $IS_CLIENT == 1 ]]; then
        DOCKER_ARGS="$DOCKER_ARGS -p 5557:5554 -p 5557:5558"
    fi

    

    
    if [[ $IS_WORKER == 0 ]]; then
        xhost +local:root
        docker run $DOCKER_ARGS -it --rm --privileged  \
            -v $PWD:/root/.torch/models \
            -v $PWD/avatars:/app/avatarify/avatars \
            --env="DISPLAY" \
            --env="QT_X11_NO_MITSHM=1" \
            --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
            avatarify python3 afy/cam_fomm.py \
                --config $FOMM_CONFIG \
                --checkpoint $FOMM_CKPT \
                --virt-cam $CAMID_VIRT \
                --relative \
                --adapt_scale \
                $@
        xhost -local:root

    else
        docker run $DOCKER_ARGS -it --rm --privileged  \
            -v $PWD:/root/.torch/models \
            -v $PWD/avatars:/app/avatarify/avatars \
            avatarify python3 afy/cam_fomm.py \
                --config $FOMM_CONFIG \
                --checkpoint $FOMM_CKPT \
                --virt-cam $CAMID_VIRT \
                --relative \
                --adapt_scale \
                $@
    fi
    

fi
