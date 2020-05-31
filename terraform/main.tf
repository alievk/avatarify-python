##################################################
# Variables
##################################################

variable "aws_profile" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "trusted_cidr_blocks" {
  type = list(string)
}

variable "ssh_public_key" {
  type = string
}

variable "ssh_private_key" {
  type = string
}

##################################################
# Provider
##################################################

terraform {
  required_providers {
    aws      = ">= 2.63.0"
    template = ">= 2.1.2"
  }
}

provider "aws" {
  profile = var.aws_profile
  region  = var.aws_region
}

##################################################
# Security policies
##################################################

resource "aws_iam_role" "avatarify" {
  name = "avatarify"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF

}

resource "aws_iam_policy_attachment" "avatarify" {
  name       = "avatarify"
  roles      = [aws_iam_role.avatarify.name]
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_instance_profile" "avatarify" {
  name = "avatarify"
  role = aws_iam_role.avatarify.name
}

resource "aws_default_vpc" "default" {}

resource "aws_security_group" "avatarify" {
  name_prefix = "avatarify"
  vpc_id      = aws_default_vpc.default.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = var.trusted_cidr_blocks
  }


  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

}

##################################################
# EC2 Instance
##################################################

resource "aws_key_pair" "avatarify" {
  key_name   = "avatarify"
  public_key = file(var.ssh_public_key)
}

resource "aws_instance" "avatarify" {
  ami           = "ami-08c757228751c5335" # ubuntu 18.04
  instance_type = "g4dn.xlarge"

  key_name             = aws_key_pair.avatarify.key_name
  iam_instance_profile = aws_iam_instance_profile.avatarify.name
  security_groups      = [aws_security_group.avatarify.name]

  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      host        = self.public_ip
      user        = "ubuntu"
      private_key = file(var.ssh_private_key)
    }

    script = "cloud-init.sh"
  }
}

output "instance_public_ip" {
  value = aws_instance.avatarify.public_ip
}
