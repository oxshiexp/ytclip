sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git ffmpeg
python3 --version
ffmpeg -version
git clone https://github.com/naufaljct48/youtube-heatmap-clipper.git
cd youtube-heatmap-clipper
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install fastapi uvicorn python-multipart
python main.py --help
nano web.py
uvicorn web:app --host 0.0.0.0 --port 8000
[200~sudo apt update && sudo apt upgrade -y~
sudo apt update && sudo apt upgrade -y
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
cd youtube-heatmap-clipper
sudo ufw allow 8000
sudo ufw reload
clear
cd home
cd root
cd streamflow
timedatectl status
timedatectl list-timezones | grep Asia
sudo timedatectl set-timezone Asia/Jakarta
pm2 restart streamflow
timedatectl status
timedatectl list-timezones | grep Asia
sudo timedatectl set-timezone Asia/Jakarta
pm2 restart streamflow
sudo apt update && sudo apt upgrade -y
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version
npm --version
sudo apt install ffmpeg -y
ffmpeg -version
sudo apt install git -y
git clone https://github.com/bangtutorial/streamflow
cd streamflow
npm install
node generate-secret.js
nano .env
npm run dev
cd streamflow
sudo ufw allow ssh
# atau jika menggunakan port custom SSH
# sudo ufw allow [PORT_SSH_ANDA]
sudo ufw allow 7575
sudo ufw status verbose
sudo ufw enable
sudo ufw status
sudo npm install -g pm2
pm2 start app.js --name streamflow
cd streamflow
npm run dev
cd streamflow
timedatectl status
PORT=7575
SESSION_SECRET=your_random_secret_here
NODE_ENV=development
docker-compose up --build
sudo apt install -y screen
screen -S app
python3 app.py
screen -r app
cd streammflow
cd streamflow
sudo ufw allow ssh
# atau jika menggunakan port custom SSH
# sudo ufw allow [PORT_SSH_ANDA]
sudo ufw allow 7575
sudo ufw enable
sudo ufw status
sudo npm install -g pm2
pm2 start app.js --name streamflow
# Simpan konfigurasi PM2 saat ini
pm2 save
# Setup PM2 untuk auto-start saat server restart
pm2 startup
# Ikuti instruksi yang muncul, biasanya berupa command yang harus dijalankan dengan sudo
# Contoh output: sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u username --hp /home/username
# Setelah menjalankan command startup, save kembali
pm2 save
curl -o install.sh https://raw.githubusercontent.com/bangtutorial/streamflow/main/install.sh && chmod +x install.sh && ./install.sh
rm -rf /root/app/*
rm -rf /root/app/.[!.]* /root/app/..?*
ls -la /root
rm streamflow
rm -rf /path/ke/streamflow
la -la /root
rm -rf /path/ke/streamflow
ls -la /path/ke/ | grep streamflow
test -d /path/ke/streamflow && echo "MASIH ADA" || echo "SUDAH TERHAPUS"
la -la /root
rm -rf /root/streamflow
type rm
/bin/rm -rf --one-file-system /root/streamflow
mount | grep /root/streamflow
/bin/rm -rf /root/streamflow
test -d /root/streamflow && echo "MASIH ADA" || echo "SUDAH TERHAPUS"
curl -o install.sh https://raw.githubusercontent.com/bangtutorial/streamflow/main/install.sh && chmod +x install.sh && ./install.sh
add -f
sudo apt update && sudo apt upgrade -y
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version
npm --version
sudo apt install ffmpeg -y
ffmpeg -version
sudo apt install git -y
git clone https://github.com/bangtutorial/streamflow
cd streamflow
npm install
node generate-secret.js
nano .env
npm run dev
cd streamflow
# Lihat status aplikasi
pm2 status
# Restart aplikasi
pm2 restart streamflow
# Stop aplikasi
pm2 stop streamflow
# Lihat logs aplikasi
pm2 logs streamflow
# Monitor resource usage
pm2 monit
cd streamflow
sudo apt install -y screen
screen -S app
python3 app.py
screen -r app
pm2 start app.js --name streamflow
cdd streamflow
pm2 start app.js --name streamflow
npm run dev
cd strreamflow
cs streamflow
cd streamflow
npm run dev
cd streamflow
npm run dev
uptime
who -b   # terakhir reboot kapan
[Unit]
Description=App 8000
After=network.target
[Service]
WorkingDirectory=/root/streamflow
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=3
[Install]
WantedBy=multi-user.target
sudo apt update && sudo apt install -y tmux
tmux new -s app
python3 app.py
nohup python3 app.py > app.log 2>&1 &
cd streamflow
pm2 status
pm2 start
pm2 restart streamflow
pm2 monit
pm2 save
pm2 startup systemd -u root --hp /root
systemctl status pm2-root --no-pager
sudo ufw allow ssh
# atau jika menggunakan port custom SSH
# sudo ufw allow [PORT_SSH_ANDA]
sudo ufw allow 7575
sudo ufw status verbose
sudo ufw enable
sudo ufw status
sudo npm install -g pm2
# Simpan konfigurasi PM2 saat ini
pm2 save
# Setup PM2 untuk auto-start saat server restart
pm2 startup
# Ikuti instruksi yang muncul, biasanya berupa command yang harus dijalankan dengan sudo
# Contoh output: sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u username --hp /home/username
# Setelah menjalankan command startup, save kembali
pm2 save
# Lihat status aplikasi
pm2 status
# Restart aplikasi
pm2 restart streamflow
# Stop aplikasi
pm2 stop streamflow
# Lihat logs aplikasi
pm2 logs streamflow
cd strreammflow
cd streamflow
timedatectl status
timedatectl list-timezones | grep Asia
sudo timedatectl set-timezone Asia/Jakarta
pm2 restart streamflow
cd /root/streamflow
pm2 start app.js --name streamflow --time --restart-delay 3000 --max-memory-restart 500M
pm2 status
pm2 logs streamflow
pm2 save
pm2 startup
systemctl status pm2-root --no-pager
ufw allow ssh
ufw allow 7575/tcp
ufw status
