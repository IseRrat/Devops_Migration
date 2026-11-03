FROM python:3.12-slim AS builder

WORKDIR /src
COPY pyproject.toml README.md LICENSE ./
COPY tinygrad/ ./tinygrad/
RUN python -m pip wheel --no-cache-dir --wheel-dir /wheels .

FROM python:3.12-slim

ARG VCS_REF=unknown
LABEL org.opencontainers.image.title="tinygrad" \
      org.opencontainers.image.revision="$VCS_REF" \
      org.opencontainers.image.source="https://git.nju.edu.cn/IseRrat/devops"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace
COPY --from=builder /wheels/ /wheels/
RUN python -m pip install --no-cache-dir /wheels/tinygrad-*.whl \
    && rm -rf /wheels \
    && python -c "from tinygrad import Tensor; assert Tensor([1, 2, 3]).shape == (3,)"

CMD ["python", "-c", "from tinygrad import Tensor; assert Tensor([1, 2, 3]).shape == (3,); print('tinygrad-ok')"]
