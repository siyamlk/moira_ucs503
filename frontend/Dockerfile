# --- build stage -----------------------------------------------------------
FROM node:20-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Baked into the static bundle at build time (Vite env vars are compile-time,
# not runtime) — override with --build-arg for a non-default API location.
ARG VITE_API_URL=http://localhost:8000/api
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# --- serve stage -------------------------------------------------------------
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
