FROM node:20-alpine AS build
WORKDIR /app
COPY package.json pnpm-workspace.yaml turbo.json ./
COPY apps/web ./apps/web
COPY packages ./packages
RUN npm i -g pnpm && pnpm install --filter @timetable/web && pnpm --filter @timetable/web build

FROM nginx:alpine
COPY --from=build /app/apps/web/dist /usr/share/nginx/html
EXPOSE 80
