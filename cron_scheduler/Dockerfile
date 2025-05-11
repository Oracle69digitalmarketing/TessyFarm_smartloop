# tessyfarm_smartloop/cron_scheduler/Dockerfile
FROM alpine:latest

# Install Docker CLI (to use 'docker exec') and a cron daemon
# 'dcron' is a simple cron daemon available in Alpine.
# 'tzdata' is for timezone support if your cron jobs are timezone sensitive.
RUN apk add --no-cache docker-cli dcron tzdata

# Copy the crontab file into the cron directory
# For dcron, this is typically /var/spool/cron/crontabs/
# Or /etc/crontabs/ if using another cron implementation (like busybox's)
# Let's use the standard location for user crontabs that dcron expects
COPY crontab /var/spool/cron/crontabs/root

# Set the timezone (Optional, but good practice)
# List timezones with 'ls /usr/share/zoneinfo' inside an alpine container
# Example for Akure, Nigeria (Africa/Lagos)
ENV TZ=Africa/Lagos
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Ensure the crontab file has the correct permissions (usually 600 for user crontabs)
RUN chmod 0600 /var/spool/cron/crontabs/root

# Command to run the cron daemon in the foreground
# For dcron, it's 'crond'. For busybox crond, it's 'crond -f -d 8'.
# dcron typically logs to syslog by default.
CMD ["crond", "-f", "-S"] # -f: foreground, -S: log to stderr (visible with docker logs)
