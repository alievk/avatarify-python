# Terraform template for deploying Avatarify on AWS

By using this template, you should be able to spawn an EC2 instance with Avatarify pre-installed as a systemd service within 5 minutes.

## Prerequisites

1. Terraform CLI >= 1.12
2. AWS CLI installed and configured
3. **Your AWS account must be allowed to create a G instance with 4 vCPUs (you can open a ticket to request a higher quota if you have reached the limit)**

## How-to

1. Verify and change the parameters in [input.tfvars](input.tfvars) according to your needs
2. Execute the following command to initialize the infrastructure

```
$ terraform apply -var-file input.tfvars
<redacted logs>
Apply complete! Resources: 7 added, 0 changed, 0 destroyed.

Outputs:

instance_public_ip = <some_ip_addr>
```

3. When the provisionning process is done, the server will be restarted. After a few seconds, you can now connect the avatarify client to the server using the `instance_public_ip` from the above output
4. (Optional) You can also ssh to the server using the `instance_public_ip` and the ssh private key configured in [input.tfvars](input.tfvars)

```
$ ssh ubuntu@<instance_public_ip> -i /path/to/private/key
```
