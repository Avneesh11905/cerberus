FROM node:24-alpine AS builder

WORKDIR /app

# Copy package files first to leverage Docker layer caching
COPY package*.json ./

# Install dependencies with BuildKit cache and skip audits/funding for faster builds
RUN --mount=type=cache,target=/root/.npm \
    npm ci --prefer-offline --no-audit --no-fund

# Copy the rest of the application
COPY . .

# Set environment variables required for the build
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Build the application
RUN npm run build

# Runner stage
FROM nginx:1.31.2-alpine AS runner

# Copy nginx configuration as a template so envsubst can inject environment variables at runtime
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Copy built assets from builder
COPY --from=builder /app/dist/client /usr/share/nginx/html

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
