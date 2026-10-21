GIT VE GITHUB KOMUTLARI — ANONİM REHBER
=========================================

1. PROJE KLASÖRÜNE GİR
----------------------
cd /d "PROJE_KLASORUNUN_YOLU"


2. GIT KULLANICI ADI VE E-POSTASINI AYARLA
-----------------------------------------
git config --global user.name "Kullanıcı Adı"

git config --global user.email "eposta@example.com"

Kullanıcı adını kontrol et:
git config --global user.name

E-posta adresini kontrol et:
git config --global user.email


3. GIT DURUMUNU KONTROL ET
--------------------------
git status

Mevcut dalları göster:
git branch

Uzak depo bağlantısını göster:
git remote -v


4. GITHUB REPOSUNA BAĞLAN
-------------------------
İlk kez bağlantı ekle:
git remote add origin REPO_URL

Mevcut bağlantıyı değiştir:
git remote set-url origin REPO_URL

Bağlantıyı kontrol et:
git remote -v


5. YENİ DOSYA EKLE VE GITHUB'A GÖNDER
-------------------------------------
git add .
git commit -m "Yeni dosya eklendi"
git push origin main


6. DOSYALARI GÜNCELLE VE GÖNDER
-------------------------------
git status
git add .
git commit -m "Dosyalar güncellendi"
git push origin main


7. COMMIT GEÇMİŞİNİ GÖR
-----------------------
git log --oneline

Yazar ve commit ayrıntılarını göster:
git log

Son commit'i incele:
git show

Değişen dosyaları göster:
git show --stat COMMIT_KODU


8. GITHUB'DAKİ DEĞİŞİKLİKLERİ AL
--------------------------------
git fetch origin

git pull --rebase origin main

Ardından:
git push origin main

Çakışma çıkarsa önce çakışmayı çöz.


9. YENİ DAL OLUŞTUR
-------------------
git switch -c yeni-dal

Dalları listele:
git branch

Durumu kontrol et:
git status


10. YENİ DALI GITHUB'A GÖNDER
-----------------------------
git add .
git commit -m "Yeni özellik eklendi"
git push -u origin yeni-dal

Sonraki gönderimlerde genellikle:
git push


11. DALLAR ARASINDA GEÇİŞ YAP
-----------------------------
Ana dala geç:
git switch main

Diğer dala geç:
git switch yeni-dal


12. DALI ANA DALLA BİRLEŞTİR
----------------------------
git switch main
git pull --rebase origin main
git merge yeni-dal
git push origin main


13. DAL SİLME
-------------
Yerel dalı sil:
git branch -d yeni-dal

Uzak dalı sil:
git push origin --delete yeni-dal


14. EN ÇOK KULLANILAN ÜÇ KOMUT
------------------------------
git add .
git commit -m "Açıklama"
git push origin main


15. GÜVENLİK NOTLARI
--------------------
- Gizli bilgileri, parolaları ve API anahtarlarını gönderme.
- git push --force komutunu dikkatli kullan.
- GitHub'da yeni değişiklikler varsa önce güncellemeleri al.
- "nothing to commit" mesajı, kaydedilecek değişiklik
  bulunmadığı anlamına gelir.
- Kullanıcı adı ve e-posta ayarları GitHub giriş hesabını
  değiştirmez.
- Commit geçmişinde yazar bilgileri bulunabilir.
