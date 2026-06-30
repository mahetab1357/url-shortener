FROM node:20-alpine AS deps
WORKDIR /build
COPY package.json package-lock.json* ./
RUN npm install

FROM deps AS dev
WORKDIR /build
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM deps AS build
WORKDIR /build
COPY . .
# Vite inlines env vars into the static bundle at build time, not at
# container runtime - this only matters for docker-compose itself; the
# browser executing this bundle is on the host, outside the compose
# network, so it must reach core-service via the host-published port
# (localhost:8000), never via the internal "core-service" hostname.
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

FROM nginx:alpine AS production
COPY --from=build /build/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
