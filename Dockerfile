# syntax=docker/dockerfile:1

# ---- Builder stage: build a wheel ------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /build

RUN pip install --no-cache-dir --upgrade pip build

COPY pyproject.toml README.md CHANGELOG.md LICENSE ./
COPY src ./src

RUN python -m build --wheel --outdir /build/dist

# ---- Runtime stage: minimal image with only the installed package ---------
FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="vitagraph" \
      org.opencontainers.image.description="Reference framework for bio-signal knowledge graphs and synthetic biological-age estimation (research/education use only)" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/Ciprian-LocalPulse/vitagraph"

# Run as a non-root user
RUN useradd --create-home --uid 1000 vitagraph
USER vitagraph
WORKDIR /home/vitagraph

COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir --user /tmp/*.whl && rm -f /tmp/*.whl

ENV PATH="/home/vitagraph/.local/bin:${PATH}" \
    PYTHONUNBUFFERED=1

VOLUME ["/home/vitagraph/outputs"]

ENTRYPOINT ["vitagraph"]
CMD ["run", "--output-dir", "/home/vitagraph/outputs"]
