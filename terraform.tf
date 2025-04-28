# Provider configuration for AWS, TLS, and local resources.
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0" # Use the latest version of the AWS provider
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0" # Use the latest version if available
    }
  }

 required_version = ">= 1.5.0" 
}


# Configure the AWS provider
provider "aws" {
  region = "us-east-2"
}

# Configure locals for consistent tagging
locals {
  tags = {
    Project = "inventory_management_system"
    Environment = "production" # Adjust as needed
    CostCenter = "default"    # Adjust as needed
  }

  # Generate a SSH key pair in local storage, creates private and public key pair
  ssh_key = tls_private_key.ssh_key
}

resource "tls_private_key" "ssh_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}


# Networking resources: VPC, subnets, security groups, internet gateway, route table.
# These are necessary to provide network connectivity for the EC2 instance and RDS instance.

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags       = local.tags
}

resource "aws_subnet" "public_subnet_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-2a"
 map_public_ip_on_launch = true
  tags       = local.tags
}

resource "aws_subnet" "public_subnet_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-east-2b"
 map_public_ip_on_launch = true
  tags       = local.tags
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
  tags   = local.tags
}


resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
  tags = local.tags
}

resource "aws_route_table_association" "public_subnet_a_association" {
  subnet_id      = aws_subnet.public_subnet_a.id
  route_table_id = aws_route_table.public_route_table.id
}
resource "aws_route_table_association" "public_subnet_b_association" {
  subnet_id      = aws_subnet.public_subnet_b.id
  route_table_id = aws_route_table.public_route_table.id
}


# Database resources: RDS instance, DB subnet group, security group, and secrets manager secret.
# Required because the code analysis indicates a SQL database dependency.

resource "aws_db_subnet_group" "default" {
 subnet_ids = [aws_subnet.public_subnet_a.id, aws_subnet.public_subnet_b.id]
  tags = local.tags

}


resource "aws_db_instance" "default" {

  identifier                = "inventory-management-system-db"
  allocated_storage        = 20 # Minimum for MySQL
  storage_type             = "gp2"
  engine                   = "mysql"
  engine_version           = "8.0" # latest version as of now
  instance_class           = "db.t3.micro"  # Smallest instance size
  db_subnet_group_name      = aws_db_subnet_group.default.name
  db_name                   = "inventory_management_system"
  username                 = "admin"  # Example username, avoid using root
  password                 = random_password.db_password.result # Use randomly generated password
  publicly_accessible       = false
  skip_final_snapshot       = true
  tags                     = local.tags

}




resource "aws_security_group" "rds_sg" {
  name        = "rds_sg"
  description = "Security group for RDS instance"
  vpc_id      = aws_vpc.main.id

  # Allow inbound traffic on port 3306 (MySQL) from the EC2 instance security group
  ingress {
    from_port        = 3306
    to_port          = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2_sg.id] # allow EC2 to access RDS
  }


  tags = local.tags
}



resource "random_password" "db_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}:?"
}


# Store database credentials in AWS Secrets Manager
resource "aws_secretsmanager_secret" "db_credentials" {
  name = "inventory_management_system/db_credentials"

}


resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
 secret_string = jsonencode({
    username = aws_db_instance.default.username,
    password = aws_db_instance.default.password,
    host     = aws_db_instance.default.address,
    port     = aws_db_instance.default.port,
    dbname   = aws_db_instance.default.identifier
  })
}

# EC2 instance, security group, and IAM role.
# These are required to run the FastAPI application.
data "aws_ami" "amazon_linux_2_latest" {
 most_recent = true
  owners      = ["amazon"] # Ensure it's owned by Amazon

  filter {
    name   = "name"
 values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}


resource "aws_key_pair" "generated_key" {
  key_name   = "inventory_management_system-key"
 public_key = local.ssh_key.public_key_openssh
}




resource "aws_security_group" "ec2_sg" {
  name        = "ec2_sg"
 description = "Security group for EC2 instance"
  vpc_id      = aws_vpc.main.id

  # Allow inbound SSH traffic from your IP
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
 cidr_blocks = ["0.0.0.0/0"] # Replace with your IP or CIDR block
  }

  # Allow inbound traffic on port 8000 from anywhere (for the application)
 ingress {
    from_port        = 8000
    to_port          = 8000
    protocol        = "tcp"
 cidr_blocks = ["0.0.0.0/0"]

  }

  # Allow all outbound traffic
 egress {
    from_port   = 0
    to_port     = 0
    protocol    = "all"
    cidr_blocks = ["0.0.0.0/0"]
  }



  tags = local.tags
}





# IAM role and instance profile for EC2 instance to access Secrets Manager
resource "aws_iam_role" "ec2_role" {
  name = "ec2_role"
 assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "ec2.amazonaws.com"
      }
      }]
  })


}


resource "aws_iam_role_policy_attachment" "secretsmanager_policy" {
  policy_arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
  role       = aws_iam_role.ec2_role.name

}

resource "aws_iam_instance_profile" "ec2_profile" {
 name = "ec2_profile"
  role = aws_iam_role.ec2_role.name

}


resource "aws_instance" "app_server" {
  ami                         = data.aws_ami.amazon_linux_2_latest.id
 instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.public_subnet_a.id
 vpc_security_group_ids      = [aws_security_group.ec2_sg.id]
  iam_instance_profile        = aws_iam_instance_profile.ec2_profile.name
 key_name                    = aws_key_pair.generated_key.key_name
  user_data = <<EOF
#!/bin/bash
# Install required packages
yum update -y
yum install git python3 python3-pip jq -y
pip3 install --upgrade pip

# Clone application repository
cd /home/ec2-user
git clone https://github.com/husain1234-a/car-rental-system/
cd car-rental-system
pip3 install -r requirements.txt

# Get database credentials from AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id inventory_management_system/db_credentials --query SecretString --output text > db_credentials.json
export DB_CREDENTIALS=$(cat db_credentials.json)

# Create a systemd service file
cat > /etc/systemd/system/inventory.service << 'EOL'
[Unit]
Description=Inventory Management System
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/car-rental-system
EnvironmentFile=/home/ec2-user/car-rental-system/.env
ExecStart=/usr/local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL

# Create environment file with database credentials
cat > /home/ec2-user/car-rental-system/.env << EOL
DB_HOST=$(echo "$DB_CREDENTIALS" | jq -r '.host')
DB_PORT=$(echo "$DB_CREDENTIALS" | jq -r '.port')
DB_USERNAME=$(echo "$DB_CREDENTIALS" | jq -r '.username')
DB_PASSWORD=$(echo "$DB_CREDENTIALS" | jq -r '.password')
DB_NAME=$(echo "$DB_CREDENTIALS" | jq -r '.dbname')
EOL

# Set proper permissions
chown ec2-user:ec2-user /home/ec2-user/car-rental-system/.env
chmod 600 /home/ec2-user/car-rental-system/.env

# Enable and start the service
systemctl daemon-reload
systemctl enable inventory.service
systemctl start inventory.service

# Clean up sensitive information
rm db_credentials.json



EOF

  tags = local.tags
}



# Output the private key to a local file with restricted permissions.

resource "local_file" "private_key" {
  filename     = "inventory_management_system_private_key.pem" # safe location
  content      = local.ssh_key.private_key_pem
  file_permission = "0600" # Only owner can read and write.


}


# Cloudwatch monitoring

resource "aws_cloudwatch_metric_alarm" "cpu_utilization_high" {
  alarm_name          = "inventory_management_system_cpu_utilization_high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
 period              = 60
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Alarm when server CPU exceeds 80%"
  dimensions = {
    InstanceId = aws_instance.app_server.id
  }

}

