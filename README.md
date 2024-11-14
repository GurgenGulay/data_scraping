# Şirket İletişim Bilgileri Web Kazıma Projesi

Bu proje, verilen şirket isimleri üzerinden Google'da arama yaparak şirketlerin iletişim sayfalarına erişip e-posta adresi ve telefon numarası gibi iletişim bilgilerini kazımayı amaçlar. Web kazıma işlemi sırasında proxy kullanılarak anonimlik sağlanmaktadır.

## SWOT Analizi


---

## Özellikler
- **Proxy Kontrolü ve Kullanımı**: Geçerli proxy adresi seçilerek bağlantı anonimleştirilmektedir.
- **Google Arama Sonuçları Üzerinden Veri Toplama**: Şirket iletişim sayfasına ulaşıp iletişim bilgileri kazılmaktadır.
- **Telefon ve E-posta Bilgisi Çekme**: Sayfadaki telefon numaraları ve e-posta adresleri düzenlenerek elde edilir.
- **Batch İşleme ve Kayıt Tutma**: İşlenen batch'ler kaydedilir, böylece işlem yeniden başlatıldığında aynı batch tekrar işlenmez.
- **Çıktıyı Excel Dosyasına Kaydetme**: Her batch işlenip tamamlandığında sonuçlar Excel dosyasına kaydedilir.

## Ağ Diyagramı


## Gerekli Paketler ve Araçlar
Proje aşağıdaki Python paketlerini kullanmaktadır:

- `selenium`
- `beautifulsoup4`
- `pandas`
- `requests`

Ayrıca, **chromedriver** aracının doğru bir şekilde bilgisayarınıza kurulmuş olması gerekmektedir.

## Kurulum
### Python Paketlerini Kurun:

```bash
pip install selenium 
```
### ChromeDriver Kurulumu:

Chrome sürümünüzle uyumlu chromedriver indirilip belirtilen dosya yoluna kaydedilmelidir.

- Kodda belirtilen proxy listesi çalışabilir ancak daha güncel proxy adreslerini sağlayarak bu listeyi genişletebilirsiniz.
  
## Kullanım
`train.xlsx` dosyasını hazırlayın ve birinci sütunda şirket isimlerini belirtin.
Proje dosyasını çalıştırarak iletişim bilgilerini kazımaya başlayın:

```python
python <dosya_adı>.py
```

## Çıktılar:
Kod, `processed_batches.txt` dosyasına işlenen batch’leri kaydeder ve her batch için bir `batch_x.xlsx` dosyası oluşturur. 
Bu dosyalarda her batch'teki şirket isimleri, URL, e-posta adresleri ve telefon numaraları listelenir.

### Fonksiyonlar
- `is_proxy_valid(proxy):` Verilen proxy'nin geçerliliğini kontrol eder.
- `load_proxies(proxy_list):` Proxy listesinden geçerli bir proxy seçer.
- `create_driver_with_proxy(valid_proxy):` Seçilen proxy ile selenium sürücüsünü başlatır.
- `scrape_google_results(search_query, driver):` Google'da arama yaparak iletişim sayfasına ulaşır ve iletişim bilgilerini kazır.
- `find_contact_info(soup):` Sayfa içeriğinden telefon numaraları ve e-posta adreslerini temizleyerek çeker.
- `save_results(results, batch_index):` Her batch için sonuçları bir Excel dosyasına kaydeder.

### Dikkat Edilmesi Gereken Noktalar
Google Arama sonuçlarına otomatik erişim yapıldığı için IP engellemeleri yaşanabilir. Proxy kullanımı bu engellemeleri önlemeye yardımcı olur ancak çok fazla istek gönderilmesi yine de geçici engellere yol açabilir.
Proxy listesi düzenli olarak güncellenmelidir; bazı proxy'ler geçersiz olabilir veya zaman aşımına uğrayabilir.

### Örnek Çıktı
Aşağıda örnek bir `batch_1.xlsx` dosyasındaki satır yapısı gösterilmektedir:

| Şirket |	URL	| E-postalar |	Telefonlar |
|--------|------|------------|-------------|
| Şirket Adı 1 |	http://site1.com/contact |	['info@site1.com'] |	['+123456789'] |
| Şirket Adı 2 | http://site2.com/iletisim |	['iletisim@site2.com'] |	['+987654321'] |
