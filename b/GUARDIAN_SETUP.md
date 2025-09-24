# Guardian Setup Guide

This guide provides step-by-step instructions for setting up Hedera Guardian with Docker for VerifiedCC integration.

## Prerequisites

- Docker Desktop installed and running
- Git (for cloning Guardian repository)
- At least 8GB RAM available for Docker containers
- Hedera testnet account credentials

## Quick Start

### 1. Clone Guardian Repository

```bash
git clone https://github.com/hashgraph/guardian.git
cd guardian
```

### 2. Configure Environment Variables

Create a `.env` file in the Guardian root directory:

```bash
# Copy the template
cp .env.template .env
```

Edit the `.env` file with your Hedera testnet credentials:

```bash
# Hedera Network Configuration
HEDERA_NET=testnet
PREUSED_HEDERA_NET=testnet

# Your Hedera Testnet Account
OPERATOR_ID=0.0.xxxxx
OPERATOR_KEY=302e020100...

# Guardian Configuration
GUARDIAN_ENV=docker
GUARDIAN_PORT=3000

# Database Configuration (defaults work for Docker)
DB_HOST=mongo
DB_DATABASE=guardian_db
```

### 3. Start Guardian Services

Use the quickstart Docker Compose configuration:

```bash
# Start all Guardian services
docker compose -f docker-compose-quickstart.yml up -d

# Check service status
docker compose -f docker-compose-quickstart.yml ps
```

### 4. Verify Guardian is Running

1. **Web Interface**: Open http://localhost:3000 in your browser
2. **API Documentation**: Visit http://localhost:3000/api-docs
3. **Health Check**: Test with curl:

```bash
curl http://localhost:3000/api/v1/settings/about
```

## Detailed Setup Steps

### Step 1: Hedera Testnet Account Setup

1. **Create Hedera Account**:
   - Visit [Hedera Portal](https://portal.hedera.com/)
   - Create a testnet account
   - Note your Account ID (format: 0.0.xxxxx)
   - Download your private key

2. **Fund Your Account**:
   - Use the [Hedera Faucet](https://portal.hedera.com/faucet) to add testnet HBAR
   - Minimum 100 HBAR recommended for Guardian operations

### Step 2: Guardian Docker Configuration

1. **System Requirements**:
   ```bash
   # Check Docker version
   docker --version  # Should be 20.10+
   docker compose version  # Should be 2.0+
   
   # Check available resources
   docker system df
   ```

2. **Guardian Services Overview**:
   - **guardian-service**: Main Guardian application
   - **mongo**: MongoDB database
   - **redis**: Redis cache
   - **nats**: Message queue
   - **vault**: HashiCorp Vault for secrets
   - **web-proxy**: Nginx reverse proxy

### Step 3: Environment Configuration

Create and configure the `.env` file:

```bash
# Hedera Network Settings
HEDERA_NET=testnet
PREUSED_HEDERA_NET=testnet

# Your Hedera Account (REQUIRED)
OPERATOR_ID=0.0.xxxxx
OPERATOR_KEY=302e020100...

# Guardian Application Settings
GUARDIAN_ENV=docker
GUARDIAN_PORT=3000
LOG_LEVEL=info

# Database Configuration
DB_HOST=mongo
DB_PORT=27017
DB_DATABASE=guardian_db
DB_USERNAME=
DB_PASSWORD=

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# NATS Configuration
NATS_HOST=nats
NATS_PORT=4222

# Vault Configuration
VAULT_HOST=vault
VAULT_PORT=8200
VAULT_TOKEN=1234
```

### Step 4: Start Guardian Services

1. **Pull Latest Images**:
   ```bash
   docker compose -f docker-compose-quickstart.yml pull
   ```

2. **Start Services**:
   ```bash
   # Start in background
   docker compose -f docker-compose-quickstart.yml up -d
   
   # Or start with logs visible
   docker compose -f docker-compose-quickstart.yml up
   ```

3. **Monitor Startup**:
   ```bash
   # Check service status
   docker compose -f docker-compose-quickstart.yml ps
   
   # View logs
   docker compose -f docker-compose-quickstart.yml logs -f guardian-service
   ```

### Step 5: Initial Guardian Configuration

1. **Access Guardian Web Interface**:
   - Open http://localhost:3000
   - You should see the Guardian login page

2. **Create Standard Registry Account**:
   - Click "Register" 
   - Select "Standard Registry" role
   - Fill in organization details
   - Complete profile setup

3. **Initialize Guardian**:
   - Complete DID (Decentralized Identifier) setup
   - Generate Verifiable Credentials
   - Wait for Hedera topic creation

### Step 6: Import Verra Policy Templates

1. **Access Policy Management**:
   - Login as Standard Registry
   - Navigate to "Policies" section

2. **Import VM0042 Policy**:
   - Click "Import Policy"
   - Upload VM0042 policy template
   - Configure for renewable energy projects

3. **Publish Policy**:
   - Review policy configuration
   - Click "Publish" to activate

## VerifiedCC Integration

### Backend Configuration

Update your VerifiedCC backend `.env` file:

```bash
# Guardian Integration
GUARDIAN_URL=http://localhost:3000
GUARDIAN_USERNAME=your_registry_username
GUARDIAN_PASSWORD=your_registry_password
GUARDIAN_SUBMISSION_ENABLED=true
GUARDIAN_DEFAULT_POLICY_ID=your_published_policy_id
```

### Test Integration

1. **Health Check**:
   ```bash
   curl http://localhost:5000/api/guardian/health
   ```

2. **List Policies**:
   ```bash
   curl http://localhost:5000/api/guardian/policies
   ```

3. **Submit Test Data**:
   ```bash
   curl -X POST http://localhost:5000/api/guardian/submit \
     -H "Content-Type: application/json" \
     -d '{"device_id": "ESP32_001", "period_hours": 24}'
   ```

## Troubleshooting

### Common Issues

1. **Guardian Won't Start**:
   ```bash
   # Check Docker resources
   docker system df
   docker system prune  # Clean up if needed
   
   # Check logs
   docker compose -f docker-compose-quickstart.yml logs guardian-service
   ```

2. **Database Connection Issues**:
   ```bash
   # Restart MongoDB
   docker compose -f docker-compose-quickstart.yml restart mongo
   
   # Check MongoDB logs
   docker compose -f docker-compose-quickstart.yml logs mongo
   ```

3. **Hedera Connection Issues**:
   - Verify your OPERATOR_ID and OPERATOR_KEY
   - Check testnet account balance
   - Ensure HEDERA_NET=testnet

4. **Port Conflicts**:
   ```bash
   # Check what's using port 3000
   netstat -an | grep 3000
   
   # Change Guardian port in .env if needed
   GUARDIAN_PORT=3001
   ```

### Useful Commands

```bash
# Stop all services
docker compose -f docker-compose-quickstart.yml down

# Stop and remove volumes (clean reset)
docker compose -f docker-compose-quickstart.yml down -v

# View resource usage
docker stats

# Access Guardian container shell
docker compose -f docker-compose-quickstart.yml exec guardian-service bash

# Backup Guardian database
docker compose -f docker-compose-quickstart.yml exec mongo mongodump --db guardian_db --out /backup
```

## Production Considerations

### Security

1. **Change Default Passwords**:
   - Update Vault token
   - Set strong database passwords
   - Use environment-specific secrets

2. **Network Security**:
   - Use HTTPS in production
   - Configure firewall rules
   - Implement proper authentication

3. **Data Backup**:
   - Regular MongoDB backups
   - Vault secret backups
   - Policy configuration exports

### Scaling

1. **Resource Allocation**:
   - Monitor CPU and memory usage
   - Scale containers as needed
   - Use Docker Swarm or Kubernetes for clustering

2. **Database Optimization**:
   - Configure MongoDB replica sets
   - Implement proper indexing
   - Monitor query performance

## Support and Resources

- **Guardian Documentation**: https://docs.hedera.com/guardian
- **Hedera Developer Portal**: https://portal.hedera.com/
- **Guardian GitHub**: https://github.com/hashgraph/guardian
- **Community Discord**: https://hedera.com/discord

## Next Steps

After Guardian is running:

1. **Configure Policies**: Set up renewable energy verification policies
2. **Create User Accounts**: Register Project Proponents and VVBs
3. **Test Workflows**: Submit sample energy data through VerifiedCC
4. **Monitor Operations**: Use Guardian dashboard and VerifiedCC logs

For VerifiedCC-specific integration, see the main project documentation.