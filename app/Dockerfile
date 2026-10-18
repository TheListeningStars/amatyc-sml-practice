# Build the static site, then serve it with nginx.
#   docker build -t amatyc-practice . && docker run -p 8080:80 amatyc-practice
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
