FROM nvcr.io/nvidia/cuda:10.0-cudnn7-runtime-ubuntu18.04

RUN DEBIAN_FRONTEND=noninteractive apt-get -qq update \
 && DEBIAN_FRONTEND=noninteractive apt-get -qqy install curl python3-pip python3-tk ffmpeg git less nano libsm6 libxext6 libxrender-dev \
 && rm -rf /var/lib/apt/lists/*

ARG PYTORCH_WHEEL="https://download.pytorch.org/whl/cu100/torch-1.0.0-cp36-cp36m-linux_x86_64.whl"
ARG FACE_ALIGNMENT_GIT="git+https://github.com/1adrianb/face-alignment"
ARG AVATARIFY_COMMIT="182bf4a10aba279cb837d6c8e6c281191114fd77"
ARG FOMM_COMMIT="efbe0a6f17b38360ff9a446fddfbb3ce5493534c"

RUN git clone https://github.com/alievk/avatarify.git /app/avatarify && cd /app/avatarify && git checkout ${AVATARIFY_COMMIT} \
 && git clone https://github.com/alievk/first-order-model.git /app/avatarify/fomm && cd /app/avatarify/fomm && git checkout ${FOMM_COMMIT}

WORKDIR /app/avatarify

RUN bash scripts/download_data.sh

RUN pip3 install ${PYTORCH_WHEEL} ${FACE_ALIGNMENT_GIT} -r requirements.txt \
 && pip3 install ${PYTORCH_WHEEL} ${FACE_ALIGNMENT_GIT} -r fomm/requirements.txt \
 && rm -rf /root/.cache/pip

ENV PYTHONPATH="/app/avatarify:/app/avatarify/fomm"

EXPOSE 5557
EXPOSE 5558

CMD ["python3", "afy/cam_fomm.py", "--config", "fomm/config/vox-adv-256.yaml", "--checkpoint", "vox-adv-cpk.pth.tar", "--virt-cam", "9", "--relative", "--adapt_scale", "--is-worker"]
