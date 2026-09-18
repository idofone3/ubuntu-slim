#!/bin/bash
# Force the hostname to 'ubuntu'
hostname ubuntu

# Start the SSH daemon in the foreground to keep the container alive
exec /usr/sbin/sshd -D
