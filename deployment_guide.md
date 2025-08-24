# 🚀 Panduan Deployment ke aaPanel dengan Apache & MySQL

## 📋 Persiapan Deployment

### 1. Persiapan Server
- Server dengan aaPanel terinstall
- Apache web server
- MySQL database
- Python 3.8+ dengan pip
- Domain atau subdomain yang sudah dikonfigurasi

### 2. Persiapan Database MySQL

#### Buat Database Baru
```sql
CREATE DATABASE daily_content CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'daily_content_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON daily_content.* TO 'daily_content_user'@'localhost';
FLUSH PRIVILEGES;
```

## 🔧 Langkah Deployment

### 1. Upload Files ke Server
Upload semua file project ke directory: `/var/www/html/daily-content/`

### 2. Setup Virtual Environment
```bash
cd /var/www/html/daily-content
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
```

### 3. Konfigurasi Environment
```bash
cp .env.example .env
nano .env
```

Edit file `.env` dengan konfigurasi production:
```env
# Database Configuration
DATABASE_URL=mysql+pymysql://daily_content_user:your_secure_password@localhost:3306/daily_content

# MySQL Database Settings
DB_HOST=localhost
DB_PORT=3306
DB_NAME=daily_content
DB_USER=daily_content_user
DB_PASSWORD=your_secure_password

# Application Settings
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=false
ENVIRONMENT=production

# File Upload Settings
UPLOAD_FOLDER=/var/www/html/daily-content/uploads
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,mp4,mov,avi

# Security Settings
CORS_ORIGINS=https://yourdomain.com
```

### 4. Inisialisasi Database
```bash
python init_database.py
```

### 5. Setup Permissions
```bash
chown -R www-data:www-data /var/www/html/daily-content
chmod -R 755 /var/www/html/daily-content
chmod -R 777 /var/www/html/daily-content/uploads
```

### 6. Konfigurasi Apache

#### Install mod_wsgi
```bash
apt-get install libapache2-mod-wsgi-py3
a2enmod wsgi
```

#### Buat Virtual Host
Copy file `apache_config.conf` ke `/etc/apache2/sites-available/daily-content.conf`

Edit sesuai domain Anda:
```apache
<VirtualHost *:443>
    ServerName yourdomain.com
    DocumentRoot /var/www/html/daily-content
    
    WSGIDaemonProcess daily_content python-path=/var/www/html/daily-content python-home=/var/www/html/daily-content/venv
    WSGIProcessGroup daily_content
    WSGIScriptAlias / /var/www/html/daily-content/wsgi.py
    
    # ... rest of configuration
</VirtualHost>
```

#### Aktifkan Site
```bash
a2ensite daily-content.conf
systemctl reload apache2
```

## 🔒 Keamanan & Optimasi

### 1. SSL Certificate
Setup SSL certificate melalui aaPanel atau Let's Encrypt:
```bash
certbot --apache -d yourdomain.com
```

### 2. Firewall Configuration
```bash
ufw allow 80
ufw allow 443
ufw allow 22
ufw enable
```

### 3. Database Security
- Gunakan password yang kuat
- Batasi akses database hanya dari localhost
- Regular backup database

### 4. File Permissions
```bash
# Set proper ownership
chown -R www-data:www-data /var/www/html/daily-content

# Set directory permissions
find /var/www/html/daily-content -type d -exec chmod 755 {} \;

# Set file permissions
find /var/www/html/daily-content -type f -exec chmod 644 {} \;

# Make scripts executable
chmod +x /var/www/html/daily-content/init_database.py
chmod +x /var/www/html/daily-content/wsgi.py
```

## 🔧 Troubleshooting

### 1. Database Connection Error
```bash
# Test database connection
python -c "from database import engine; print('Database connection OK')"
```

### 2. Permission Issues
```bash
# Fix upload directory permissions
chmod 777 /var/www/html/daily-content/uploads
chown www-data:www-data /var/www/html/daily-content/uploads
```

### 3. Playwright Browser Issues
```bash
# Install system dependencies
apt-get update
apt-get install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2

# Reinstall browsers
source venv/bin/activate
playwright install
```

### 4. Apache Logs
```bash
# Check Apache error logs
tail -f /var/log/apache2/daily_content_error.log

# Check access logs
tail -f /var/log/apache2/daily_content_access.log
```

## 📊 Monitoring & Maintenance

### 1. Health Check
Akses: `https://yourdomain.com/health`

### 2. Log Monitoring
```bash
# Application logs
tail -f /var/log/apache2/daily_content_error.log

# System logs
journalctl -u apache2 -f
```

### 3. Database Backup
```bash
# Create backup script
cat > /var/www/html/daily-content/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u daily_content_user -p daily_content > /var/backups/daily_content_$DATE.sql
find /var/backups -name "daily_content_*.sql" -mtime +7 -delete
EOF

chmod +x /var/www/html/daily-content/backup.sh

# Add to crontab
echo "0 2 * * * /var/www/html/daily-content/backup.sh" | crontab -
```

### 4. Update Deployment
```bash
cd /var/www/html/daily-content
git pull origin main  # if using git
source venv/bin/activate
pip install -r requirements.txt
systemctl reload apache2
```

## ✅ Verifikasi Deployment

1. **Database Connection**: Akses `/health` endpoint
2. **File Upload**: Test upload konten melalui dashboard
3. **Static Files**: Pastikan CSS/JS loading dengan benar
4. **SSL Certificate**: Verify HTTPS working
5. **Browser Automation**: Test publish functionality

## 🆘 Support

Jika mengalami masalah:
1. Check Apache error logs
2. Verify database connection
3. Check file permissions
4. Test individual components
5. Review environment variables

---

**🎉 Selamat! Aplikasi Daily Content Uploader sudah siap production di aaPanel!**
