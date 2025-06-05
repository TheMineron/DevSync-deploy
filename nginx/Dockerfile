FROM node:18-alpine as build

WORKDIR /frontend
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend .
RUN npm run build

FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY --from=build /frontend/dist /usr/share/nginx/html
COPY ./nginx/nginx.conf /etc/nginx/conf.d
COPY ./nginx/proxy_params /etc/nginx
RUN mkdir -p /etc/nginx/ssl/
COPY ./nginx/ssl/certificate.key /etc/nginx/ssl/certificate.key
COPY ./nginx/ssl/fullchain.pem /etc/nginx/ssl/fullchain.pem
