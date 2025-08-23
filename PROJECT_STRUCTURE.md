# Enhanced OSINT System v2.0 - Project Structure

## 📁 Clean Repository Structure

```
enhanced-osint-system-v2/
├── 📄 README.md                    # Main project documentation
├── 📄 PROJECT_STRUCTURE.md         # This file - project organization
├── 📄 .gitignore                   # Git ignore rules
├── 📄 .env.example                 # Environment variables template
├── 📄 requirements.txt             # Python dependencies
├── 📄 Dockerfile                   # Docker container configuration
├── 📄 docker-compose.yaml          # Docker Compose for deployment
├── 📄 main.py                      # Flask web service entry point
├── 📄 test_pocketbase.py          # PocketBase connection test
├── 📄 deploy-coolify.sh           # Deployment script for Coolify
├── 📁 config/                      # Configuration management
│   └── 📄 settings.py              # Centralized configuration
├── 📁 core/                        # Core application logic
│   ├── 📄 enrichment.py           # Main OSINT enrichment pipeline
│   └── 📄 pocketbase_client.py    # PocketBase database client
├── 📁 osint-tools/                 # OSINT utility modules
│   ├── 📄 dns_utils.py            # DNS lookup utilities
│   ├── 📄 whois_utils.py          # WHOIS lookup utilities
│   ├── 📄 social_media.py         # Social media profile detection
│   └── 📄 validators.py           # Email and domain validation
├── 📁 logs/                        # Application logs (gitignored)
└── 📁 scripts/                     # Utility scripts
```

## 🎯 Key Benefits of Clean Structure

### ✅ **What We Fixed:**
1. **Eliminated duplicate files** - No more conflicting versions
2. **Proper naming conventions** - `docker-compose.yaml` (not `.yml`)
3. **Comprehensive .gitignore** - Prevents future clutter
4. **Clear documentation** - Professional README and structure docs
5. **Focused codebase** - Only production-ready files

### ❌ **What We Removed:**
- Old test files (`test_*.py`, `*_test.py`)
- Generated data files (`*.json` results)
- Duplicate configurations
- Legacy scripts and versions
- Temporary files and logs

## 🚀 Development Workflow

### **Adding New Features**
1. Create feature branch: `git checkout -b feature/name`
2. Follow file size limit: **< 200 lines per file**
3. Use proper error handling and logging
4. Add tests in separate test files (gitignored)
5. Update documentation if needed

### **File Organization**
- **`core/`**: Main business logic
- **`osint-tools/`**: Reusable OSINT utilities  
- **`config/`**: Configuration and settings
- **`scripts/`**: Deployment and utility scripts

## 🔧 Configuration Management

All configuration is centralized in `config/settings.py` using dataclasses:

```python
@dataclass
class DatabaseConfig:
    url: str
    email: str
    password: str

@dataclass
class ProcessingConfig:
    max_workers: int = 80
    batch_size: int = 5000
```

## 🐳 Deployment

The clean structure ensures:
- **Predictable builds**: No conflicting files
- **Faster deployments**: Smaller, focused codebase
- **Easier debugging**: Clear file organization
- **Better maintenance**: Logical separation of concerns

## 📊 Quality Standards

### **Code Quality**
- Type hints for all functions
- Comprehensive error handling
- Descriptive logging with termcolor
- UTF-8 encoding for file operations

### **Documentation**
- Clear README with badges and examples
- Inline code documentation
- API endpoint documentation
- Deployment instructions

## 🧹 Maintenance

### **Regular Cleanup**
```bash
# Remove generated files
git clean -fd

# Check for large files
git ls-files | xargs ls -la | sort -k5 -rn | head

# Update .gitignore as needed
```

### **Monitoring**
- Application logs in `logs/` directory
- Health checks via `/health` endpoint
- Processing status via `/status` endpoint

This clean structure prevents the issues we encountered and ensures smooth development and deployment! 🎯