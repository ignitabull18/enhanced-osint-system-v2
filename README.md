# Enhanced OSINT System v2.0

A comprehensive OSINT (Open Source Intelligence) system for lead enrichment and business intelligence.

## Features

- **Advanced Lead Scoring**: Intelligent lead prioritization based on multiple factors
- **Business Intelligence**: Comprehensive company and contact analysis
- **Parallel Processing**: High-performance processing with configurable worker pools
- **PocketBase Integration**: Modern database backend for data storage
- **Flask Web Service**: RESTful API for job management and monitoring
- **Coolify Deployment**: Production-ready containerized deployment

## Quick Start

1. **Environment Variables**:
   ```bash
   POCKETBASE_URL=https://pocketbase.ignitabull.org
   POCKETBASE_EMAIL=jeremy@ignitabull.com
   POCKETBASE_PASSWORD=your_password
   MAX_WORKERS=80
   BATCH_SIZE=5000
   PORT=8002
   ```

2. **API Endpoints**:
   - `GET /` - System information
   - `GET /health` - Health check
   - `GET /status` - Processing status
   - `POST /process` - Start OSINT job

3. **Deployment**:
   ```bash
   docker build -t enhanced-osint .
   docker run -p 8002:8002 enhanced-osint
   ```

## Architecture

- **Flask Web Service**: Main application entry point
- **OSINT Core**: Parallel processing engine
- **PocketBase Client**: Database integration layer
- **Configuration**: Environment-based settings management

## Status

🚀 **Deployment Status**: Ready for Coolify deployment
✅ **Environment Variables**: Configured
✅ **Port Configuration**: 8002
✅ **Health Checks**: Enabled
✅ **PocketBase**: Integrated