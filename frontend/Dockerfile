# OmniLife AI - frontend image: build the React (Vite) app, serve with nginx.
# Works once Member 1 has created the Vite project in this folder
# (package.json must exist).
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# Backend address as seen from the user's BROWSER
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
# Single page app: unknown paths must fall back to index.html (React Router)
RUN printf 'server {\n  listen 80;\n  root /usr/share/nginx/html;\n  location / { try_files $uri /index.html; }\n}\n' > /etc/nginx/conf.d/default.conf
EXPOSE 80
