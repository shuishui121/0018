FROM node:20-alpine AS builder
WORKDIR /app

# 使用国内镜像加速
RUN npm config set registry https://registry.npmmirror.com

COPY package*.json ./
RUN npm ci || npm install

COPY . .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
