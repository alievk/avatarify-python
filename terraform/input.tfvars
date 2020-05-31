# awscli configs
aws_profile = "default"
aws_region  = "eu-west-3"

# IP ranges that are allowed to connect to any port of the server
# Default value : any ip address /!\
trusted_cidr_blocks = ["0.0.0.0/0"]

# Paths to the ssh public + private key used to connect to the server
ssh_private_key = "id"
ssh_public_key  = "id.pub"
