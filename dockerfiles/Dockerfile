ARG NV_CUDA_VERSION=13.1.1-cudnn-devel-ubuntu24.04
ARG PY_VERSION=3.12

FROM nvidia/cuda:${NV_CUDA_VERSION}

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_LINK_MODE=copy UV_PROJECT_ENVIRONMENT=/opt/venv/xfiles

ARG PY_VERSION
RUN uv venv --python ${PY_VERSION} ${UV_PROJECT_ENVIRONMENT}

RUN --mount=type=bind,source=packages/xfiles,target=/code/xfiles,rw \
    uv sync --no-install-project --all-extras -p ${UV_PROJECT_ENVIRONMENT}/bin/python --directory /code/xfiles
