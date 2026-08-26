FROM oven/bun:1-slim AS development

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        bash \
    && curl -1sLf 'https://artifacts-cli.infisical.com/setup.deb.sh' | bash \
    && apt-get install -y --no-install-recommends infisical \
    && rm -rf /var/lib/apt/lists/*

COPY package.json bun.lock ./

# Install all dependencies, including development dependencies
RUN bun install --frozen-lockfile

COPY . .

ENTRYPOINT ["bash", "-c", "if [ -n \"$INFISICAL_MACHINE_IDENTITY_CLIENT_ID\" ] && [ -z \"$INFISICAL_TOKEN\" ]; then export INFISICAL_TOKEN=$(infisical login --method=universal-auth --client-id=\"$INFISICAL_MACHINE_IDENTITY_CLIENT_ID\" --client-secret=\"$INFISICAL_MACHINE_IDENTITY_CLIENT_SECRET\" --plain --silent); fi; if [ -n \"$INFISICAL_TOKEN\" ]; then exec infisical run --projectId \"$INFISICAL_PROJECT_ID\" --env=\"${INFISICAL_ENVIRONMENT:-dev}\" --path=/ -- \"$@\"; else exec \"$@\"; fi", "--"]

CMD ["bun", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]