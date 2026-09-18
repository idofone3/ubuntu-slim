# Use the official Debian slim image
FROM debian:stable-slim

# Install OpenSSH server
RUN apt-get update && \
    apt-get install -y openssh-server && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create the privilege separation directory required by sshd
# -p prevents the error if the directory already exists in the base image
RUN mkdir -p /var/run/sshd

# Set up user 'ash' with password 'root'
RUN useradd -rm -d /home/ash -s /bin/bash ash && \
    echo "ash:root" | chpasswd

# Configure SSH daemon
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config

# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the standard SSH port
EXPOSE 22

# Run the entrypoint script which sets the hostname and starts SSH
CMD ["/entrypoint.sh"]
