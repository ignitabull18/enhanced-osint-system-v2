# Enhanced OSINT System v2.0 - Coolify Deployment

🚀 **Enterprise-grade OSINT enrichment system optimized for Coolify deployment**

## 📋 Overview

The Enhanced OSINT System v2.0 is a production-ready lead enrichment platform that processes large datasets with parallel processing, advanced scoring, and business intelligence analysis. This package is specifically optimized for Coolify deployment with enterprise features.

## ✨ Features

- **80-Worker Parallel Processing**: Process thousands of leads simultaneously
- **Advanced Scoring Engine**: Multi-dimensional lead scoring and prioritization
- **Business Intelligence**: Portfolio analysis and strategic recommendations
- **Enterprise Monitoring**: Health checks, logging, and performance metrics
- **Coolify Optimized**: Built for production deployment and scaling
- **OSINT Tools**: Email validation, WHOIS lookup, DNS analysis, social media discovery

## 🏗️ Architecture

```
enhanced-osint-coolify/
├── osint-tools/           # OSINT utility modules
│   ├── dns_utils.py      # DNS lookup and analysis
│   ├── whois_utils.py    # WHOIS data retrieval
│   ├── social_media.py   # Social media profile discovery
│   └── validators.py     # Email and data validation
├── core/                  # Core processing modules
│   ├── pipeline.py       # Main enrichment pipeline
│   └── enrichment.py     # Parallel processing engine
├── config/                # Configuration management
│   └── settings.py       # Centralized configuration
├── scripts/               # Utility scripts
├── logs/                  # Application logs
├── Dockerfile            # Coolify-optimized container
├── docker-compose.yml    # Local development setup
└── main.py               # Application entry point
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- PocketBase instance (self-hosted on Coolify)
- Coolify instance (for production deployment)

### Local Development

1. **Clone and setup:**
   ```bash
   cd enhanced-osint-coolify
   cp .env.example .env
   # Edit .env with your PocketBase credentials
   ```

2. **Build and run:**
   ```bash
   docker-compose up --build
   ```

3. **Monitor logs:**
   ```bash
   docker-compose logs -f enhanced-osint
   ```

### Coolify Deployment

1. **Connect your repository to Coolify**
2. **Set environment variables:**
   - `POCKETBASE_URL`: Your PocketBase instance URL
   - `POCKETBASE_EMAIL`: Your PocketBase admin email
   - `POCKETBASE_PASSWORD`: Your PocketBase admin password
   - `MAX_WORKERS`: Number of parallel workers (default: 80)
   - `BATCH_SIZE`: Lead batch size (default: 5000)
   - `LOG_LEVEL`: Logging level (default: INFO)

3. **Deploy and monitor through Coolify dashboard**

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POCKETBASE_URL` | PocketBase instance URL | Required |
| `POCKETBASE_EMAIL` | PocketBase admin email | Required |
| `POCKETBASE_PASSWORD` | PocketBase admin password | Required |
| `MAX_WORKERS` | Parallel processing workers | 80 |
| `BATCH_SIZE` | Lead batch size | 5000 |
| `LOG_LEVEL` | Logging level | INFO |
| `ENVIRONMENT` | Deployment environment | production |

### Processing Configuration

- **Max Workers**: 80 parallel workers for optimal performance
- **Batch Size**: Configurable from 1000 to 50,000+ leads
- **Timeout Settings**: Configurable timeouts for each OSINT tool
- **Retry Logic**: Automatic retry with exponential backoff

## 📊 Performance

### Processing Speeds

| Batch Size | 80 Workers | Sequential | Speedup |
|------------|------------|------------|---------|
| 1,000      | ~30 min    | ~10 hours  | 20x     |
| 5,000      | ~6 hours   | ~50 hours  | 8x      |
| 10,000     | ~12 hours  | ~100 hours | 8x      |
| 25,000     | ~30 hours  | ~250 hours | 8x      |

### Resource Requirements

- **CPU**: 2-4 cores recommended
- **Memory**: 2-4GB RAM minimum
- **Storage**: 1-5GB depending on batch size
- **Network**: Stable internet for OSINT tool APIs

## 🔍 Monitoring & Health Checks

### Health Check Endpoint

The system provides a health check endpoint at `/health` for Coolify monitoring:

```json
{
  "status": "healthy",
  "timestamp": 1640995200,
  "version": "2.0.0",
  "environment": "production",
  "config": {
    "max_workers": 80,
    "batch_size": 5000
  }
}
```

### Logging

- **Structured Logging**: JSON-formatted logs for easy parsing
- **File Rotation**: Automatic log rotation and management
- **Log Levels**: Configurable logging levels (DEBUG, INFO, WARNING, ERROR)
- **Performance Metrics**: Processing time and throughput logging

## 🛠️ Development

### Local Testing

```bash
# Run with custom configuration
MAX_WORKERS=40 BATCH_SIZE=1000 python main.py

# Run with debug logging
LOG_LEVEL=DEBUG python main.py
```

### Adding New OSINT Tools

1. Create tool module in `osint-tools/`
2. Add configuration in `config/settings.py`
3. Integrate with main pipeline in `core/pipeline.py`
4. Update requirements.txt if needed

## 🚨 Troubleshooting

### Common Issues

1. **WHOIS Timeouts**: Increase `WHOIS_TIMEOUT` environment variable
2. **Memory Issues**: Reduce `MAX_WORKERS` or increase container memory
3. **Network Errors**: Check firewall and proxy settings
4. **Database Connection**: Verify PocketBase credentials and network access

### Debug Mode

Enable debug mode for detailed logging:

```bash
DEBUG=true LOG_LEVEL=DEBUG docker-compose up
```

## 📈 Scaling

### Horizontal Scaling

- **Multiple Instances**: Deploy multiple containers across servers
- **Load Balancing**: Use Coolify's built-in load balancing
- **Database Sharding**: Partition data across multiple PocketBase instances

### Vertical Scaling

- **Resource Allocation**: Increase CPU/memory allocation in Coolify
- **Worker Optimization**: Adjust `MAX_WORKERS` based on server capacity
- **Batch Size Tuning**: Optimize batch size for your infrastructure

## 🔒 Security

- **Non-root User**: Container runs as non-root user
- **Environment Variables**: Sensitive data stored in environment variables
- **Network Isolation**: Containerized deployment with network isolation
- **Input Validation**: All inputs validated and sanitized

## 📞 Support

For issues and questions:

1. Check the logs for error details
2. Verify configuration and environment variables
3. Test with smaller batch sizes first
4. Monitor resource usage and performance metrics

## 🎯 Roadmap

- **v2.1**: Redis integration for job queuing
- **v2.2**: Webhook notifications and API endpoints
- **v2.3**: Advanced analytics and reporting dashboard
- **v2.4**: Machine learning-powered scoring improvements

---

**Built for production. Optimized for scale. Ready for Coolify.** 🚀
