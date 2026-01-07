FROM pathwaycom/pathway:latest

WORKDIR /app

# Install nginx, supervisor, and PostgreSQL libraries
RUN apt-get update && \
    apt-get install -y nginx supervisor postgresql-client libpq-dev && \
    pip install psycopg2-binary && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /var/log/supervisor

# Copy application files
COPY app/ /app/
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create directories
RUN mkdir -p /app/output /app/web

EXPOSE 8000

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]