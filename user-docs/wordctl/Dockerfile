# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy source (single file + top-level dirs)
COPY wordctl.py /app/
COPY commands /app/commands
COPY store /app/store

# Expose 'wordctl' as the container command
RUN printf '#!/usr/bin/env sh\nexec python /app/wordctl.py "$@"\n' > /usr/local/bin/wordctl \
  && chmod +x /usr/local/bin/wordctl

ENTRYPOINT ["wordctl"]
