# Use the official Debian slim image
FROM debian:stable-slim

# Install OpenSSH server and sudo
RUN apt-get update && \
    apt-get install -y openssh-server sudo && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create the privilege separation directory required by sshd
RUN mkdir -p /var/run/sshd

# Set up user 'ash' with password 'root' and add to sudo group
RUN useradd -rm -d /home/ash -s /bin/bash ash && \
    echo "ash:root" | chpasswd && \
    usermod -aG sudo ash

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
