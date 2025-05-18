FROM nginx:alpine

# Copy all application files
COPY . /usr/share/nginx/html/

# Fix permissions
RUN chmod -R 755 /usr/share/nginx/html/

# Create a proper nginx configuration
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location /static/ { \
        add_header Cache-Control "public, max-age=31536000"; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
