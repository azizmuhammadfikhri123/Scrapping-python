## Run file python with cron job

### Persyaratan
  - Pastikan sudah install python
  - Pastikan install semua library dan sesuaikan
    
### Langkah 1: Clone Repositori
  - git clone https://github.com/azizmuhammadfikhri123/Scrapping-python.git
  - cd Scrapping-python

### Langkah 2: Atur cron job 
   - Buka terminal
   - Ketikan crontab -e
   - Tambahkan baris * * * * * /path/to/python3 /path/to/your/multi.py
   - Sesuaikan path python dan path file python yang ingin di jalankan
   - setelah itu save

### Program akan berjalan setiap menit sekali dan akan menghasilkan file scraper_log.txt
  
