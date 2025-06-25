# 🚀 Deployment Guide - Intelligent RAG Assistant

**Author:** Sreevallabh kakarala  
**Version:** 2.0  
**Last Updated:** December 2024

---

## 📋 Pre-Deployment Checklist

- [ ] **System Requirements Met**
  - [ ] Python 3.8+ installed
  - [ ] 8GB+ RAM available
  - [ ] 5GB+ storage space
  - [ ] Stable internet connection

- [ ] **Dependencies Ready**
  - [ ] All required files present
  - [ ] Requirements files updated
  - [ ] Configuration files reviewed

- [ ] **Optional Components**
  - [ ] Docker installed (for containerized deployment)
  - [ ] Cloud CLI tools installed (if deploying to cloud)

---

## 🎯 Deployment Options

### **Option 1: Local Production Deployment** 
*Recommended for development and local hosting*

#### Quick Start
```bash
# Windows
.\deploy-local.bat

# Manual steps
pip install -r requirements-prod.txt
ollama serve
ollama pull mistral:latest
streamlit run main.py --server.port 8501 --server.headless true
```

#### Features
- ✅ **Fast Setup**: One-click deployment
- ✅ **Local Control**: Complete system control
- ✅ **No External Dependencies**: Works offline
- ✅ **Free**: No hosting costs

#### Access
- **URL**: http://localhost:8501
- **Logs**: Console output
- **Management**: Direct file system access

---

### **Option 2: Docker Deployment**
*Recommended for consistent environments and easy scaling*

#### Quick Start
```bash
# Windows
.\deploy-docker.bat

# Manual steps
docker build -t rag-assistant:latest .
docker run -d --name rag-assistant-container -p 8501:8501 rag-assistant:latest
```

#### Features
- ✅ **Isolation**: Containerized environment
- ✅ **Consistency**: Same environment everywhere
- ✅ **Security**: Non-root user execution
- ✅ **Scalability**: Easy to replicate

#### Management
```bash
# View logs
docker logs -f rag-assistant-container

# Stop container
docker stop rag-assistant-container

# Restart container
docker restart rag-assistant-container

# Remove container
docker rm rag-assistant-container
```

---

### **Option 3: Cloud Deployment**

#### **3a. Azure Container Instances**
*Recommended for enterprise deployments*

```bash
# Prerequisites
az login
az group create --name rag-assistant-rg --location eastus

# Deploy
az container create --resource-group rag-assistant-rg --file deploy-azure.yml

# Get URL
az container show --resource-group rag-assistant-rg --name rag-assistant-aci --query ipAddress.fqdn
```

**Features:**
- ✅ **Enterprise-Grade**: High availability
- ✅ **Managed**: No server maintenance
- ✅ **Scalable**: Auto-scaling options
- ✅ **Secure**: Enterprise security features

**Cost:** ~$50-100/month for standard configuration

#### **3b. Digital Ocean**
*Recommended for cost-effective cloud hosting*

```bash
# Prerequisites
doctl auth init

# Deploy
chmod +x deploy-digitalocean.sh
./deploy-digitalocean.sh
```

**Features:**
- ✅ **Cost-Effective**: Competitive pricing
- ✅ **Simple**: Easy management interface
- ✅ **Reliable**: 99.99% uptime SLA
- ✅ **Global**: Multiple data centers

**Cost:** ~$24/month for 2 vCPU, 4GB RAM

#### **3c. Heroku**
*Recommended for quick cloud deployment*

```bash
# Prerequisites
heroku login
heroku create rag-assistant-sreevallabh

# Deploy
git add .
git commit -m "Deploy RAG Assistant"
git push heroku main
```

**Features:**
- ✅ **Zero Config**: Automatic deployment
- ✅ **Git Integration**: Deploy with git push
- ✅ **Add-ons**: Easy service integration
- ✅ **Free Tier**: Available for testing

**Cost:** Free tier available, Standard plans from $25/month

---

## 🔧 Configuration Options

### **Environment Variables**
Create `.env` file for custom configuration:

```env
# Application Settings
ENVIRONMENT=production
APP_TITLE="RAG Assistant by Sreevallabh kakarala"

# Model Configuration
OLLAMA_MODEL=mistral:latest
OLLAMA_HOST=localhost:11434

# Processing Settings
CHUNK_SIZE=400
CHUNK_OVERLAP=100
MAX_SEARCH_RESULTS=10

# UI Settings
THEME_COLOR=#667eea

# Security Settings
MAX_FILE_SIZE=100
SESSION_TIMEOUT=3600
```

### **Performance Tuning**

#### **Memory Optimization**
```python
# For systems with limited RAM
EMBEDDING_BATCH_SIZE=16  # Reduce from 32
CHUNK_SIZE=300          # Reduce from 400
```

#### **Model Selection**
```bash
# For lower RAM systems
ollama pull llama3.2:1b    # 1.5GB RAM
ollama pull llama3.2:3b    # 3GB RAM

# For high performance
ollama pull mistral:latest  # 4GB RAM (default)
```

---

## 🛡 Security Configuration

### **Production Security**
```env
# Security settings for production
ENABLE_HTTPS=true
SESSION_TIMEOUT=1800
MAX_FILE_SIZE=50

# CORS settings
STREAMLIT_SERVER_ENABLE_CORS=false
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
```

### **Network Security**
- **Local**: Bind to 127.0.0.1 for localhost only
- **LAN**: Bind to 0.0.0.0 for network access
- **Production**: Use reverse proxy (nginx) with SSL

### **Data Protection**
- ✅ **Local Processing**: No data sent externally
- ✅ **Temporary Storage**: Files deleted after processing
- ✅ **Memory Only**: No persistent data storage
- ✅ **Secure Defaults**: Conservative security settings

---

## 📊 Monitoring & Maintenance

### **Health Monitoring**
```bash
# Check application status
curl http://localhost:8501/_stcore/health

# Monitor resource usage
htop  # Linux/macOS
taskmgr  # Windows

# Docker monitoring
docker stats rag-assistant-container
```

### **Log Management**
```bash
# Application logs
tail -f logs/rag_assistant.log

# Docker logs
docker logs -f rag-assistant-container

# System logs
journalctl -u rag-assistant  # Linux systemd
```

### **Backup & Recovery**
```bash
# Backup configuration
cp config.py config.py.backup
cp .env .env.backup

# Export container
docker export rag-assistant-container > rag-assistant-backup.tar

# Import container
docker import rag-assistant-backup.tar
```

---

## 🚨 Troubleshooting

### **Common Issues**

#### **Port Already in Use**
```bash
# Find process using port 8501
netstat -ano | findstr :8501  # Windows
lsof -i :8501                 # Linux/macOS

# Kill process
taskkill /PID <PID> /F        # Windows
kill -9 <PID>                 # Linux/macOS
```

#### **Ollama Not Responding**
```bash
# Restart Ollama service
ollama serve

# Check Ollama status
ollama list

# Pull model again
ollama pull mistral:latest
```

#### **Memory Issues**
```bash
# Check memory usage
free -h                       # Linux
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /format:table  # Windows

# Use smaller model
ollama pull llama3.2:1b
```

#### **Docker Issues**
```bash
# Restart Docker service
sudo systemctl restart docker  # Linux
# Restart Docker Desktop        # Windows/macOS

# Clean Docker system
docker system prune -a
```

### **Performance Optimization**

#### **Slow Response Times**
1. **Check Model**: Ensure correct model is loaded
2. **Memory**: Verify sufficient RAM available
3. **CPU**: Monitor CPU usage during processing
4. **Storage**: Use SSD for faster model loading

#### **High Memory Usage**
1. **Reduce Batch Size**: Lower `EMBEDDING_BATCH_SIZE`
2. **Smaller Chunks**: Reduce `CHUNK_SIZE`
3. **Model Selection**: Use `llama3.2:1b` for lower RAM
4. **Container Limits**: Set Docker memory limits

---

## 📈 Scaling & Load Balancing

### **Horizontal Scaling**
```bash
# Docker Swarm
docker swarm init
docker service create --name rag-assistant --replicas 3 -p 8501:8501 rag-assistant:latest

# Kubernetes
kubectl apply -f k8s-deployment.yml
kubectl scale deployment rag-assistant --replicas=3
```

### **Load Balancing**
```nginx
# Nginx configuration
upstream rag_backend {
    server 127.0.0.1:8501;
    server 127.0.0.1:8502;
    server 127.0.0.1:8503;
}

server {
    listen 80;
    server_name rag-assistant.yourdomain.com;
    
    location / {
        proxy_pass http://rag_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🎯 Deployment Recommendations

### **Development**
- **Local Deployment**: Use `deploy-local.bat`
- **Hot Reload**: Use `streamlit run main.py --server.runOnSave true`
- **Debug Mode**: Set `ENVIRONMENT=development`

### **Staging**
- **Docker**: Use containerized deployment
- **Resource Limits**: Set memory/CPU constraints
- **Monitoring**: Enable detailed logging

### **Production**
- **Cloud Deployment**: Azure/Digital Ocean recommended
- **HTTPS**: Enable SSL/TLS encryption
- **Monitoring**: Implement comprehensive monitoring
- **Backup**: Regular configuration backups
- **Scaling**: Plan for load balancing

---

## 📞 Support

### **Deployment Issues**
- **GitHub Issues**: [Issues](https://github.com/sreevallabh04/intelligent-rag-assistant/issues)
- **Documentation**: [Wiki](https://github.com/sreevallabh04/intelligent-rag-assistant/wiki)
- **Email**: [srivallabhkakarala@gmail.com](mailto:srivallabhkakarala@gmail.com)

### **Cloud Provider Support**
- **Azure**: [Azure Support](https://azure.microsoft.com/en-us/support/)
- **Digital Ocean**: [DO Support](https://www.digitalocean.com/support/)
- **Heroku**: [Heroku Support](https://help.heroku.com/)

---

**© 2024 Sreevallabh kakarala. All rights reserved.** 