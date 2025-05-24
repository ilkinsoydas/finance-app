# Portföy Yönetim Uygulaması (Türkçe)

Bu masaüstü uygulaması, kullanıcıların döviz ve altın varlıklarını yönetmelerine, güncel ve geçmiş kur bilgilerini takip etmelerine, varlıklarının kar/zarar durumlarını ve dağılımlarını görsel olarak izlemelerine olanak tanır.

## Amaç

Uygulamanın temel amacı, bireysel kullanıcıların finansal portföylerini kolayca takip edebilmeleri için kullanıcı dostu bir arayüz sunmaktır. Kullanıcılar, farklı türdeki varlıklarını (Dolar, Euro, Sterlin, Gram Altın vb.) ekleyebilir, bu varlıkların güncel piyasa değerlerini görebilir ve geçmiş işlemlerini analiz edebilirler.

## Özellikler

* **Varlık Ekleme:** Farklı döviz türleri (USD, EUR, GBP) ve altın çeşitleri (Gram Altın, Çeyrek Altın vb.) eklenebilir.
* **Güncel Kur Bilgileri:** Anlık döviz ve altın alış/satış fiyatları listelenir.
* **Geçmiş Kur Grafikleri:** Seçilen bir döviz cinsi için son 1, 7 veya 30 günlük kur değişim grafiği görüntülenebilir.
* **Portföy Dağılımı:** Kullanıcının toplam varlığının TL cinsinden değeri ve varlık türlerine göre dağılımı pasta grafikle gösterilir.
* **Geçmiş İşlemler:**
    * Belirli bir varlık türü için yapılan tüm alım işlemleri listelenir.
    * Her bir işlem için alım tarihi, miktarı, o günkü maliyet (adet başı), geçen gün sayısı gösterilir.
    * Her bir işlem için anlık kura göre kar/zarar durumu (yüzdesel ve TL olarak) hesaplanır.
    * Seçilen varlık türü için toplam kar/zarar durumu görüntülenir.
    * Seçilen varlık türünün alım işlemlerine ait günlük TL değerleri çizgi grafikle gösterilir.
* **Veri Saklama:** Tüm varlık ve işlem bilgileri lokal bir SQLite veritabanında saklanır.
* **Kullanıcı Dostu Arayüz:** Tkinter kütüphanesi ile geliştirilmiş, kolay anlaşılır bir arayüze sahiptir.

## Kullanılan Teknolojiler

* **Programlama Dili:** Python 3
* **Arayüz (GUI):** Tkinter, ttk
* **Veri Çekme (API):** requests
* **Veritabanı:** SQLite3
* **Grafikleme:** Matplotlib
* **Tarih/Zaman İşlemleri:** datetime

## API Entegrasyonları

Uygulama, güncel ve geçmiş kur bilgilerini çekmek için aşağıdaki API'leri kullanır:

1.  **CollectAPI (Güncel Kurlar İçin):**
    * **Döviz Kurları:**
        * Endpoint: `https://api.collectapi.com/economy/allCurrency`
        * Kullanım: USD, EUR, GBP gibi popüler döviz kurlarının anlık alış ve satış fiyatlarını almak için kullanılır.
    * **Altın Fiyatları:**
        * Endpoint: `https://api.collectapi.com/economy/goldPrice`
        * Kullanım: Gram Altın, Çeyrek Altın gibi altın türlerinin anlık alış ve satış fiyatlarını almak için kullanılır.
    * **API Anahtarı:** Bu API'yi kullanmak için `YOUR_API_KEY` olarak belirtilen yere CollectAPI'den aldığınız kendi API anahtarınızı girmeniz gerekmektedir.

2.  **FreeCurrencyAPI (Geçmiş Kurlar İçin):**
    * **Geçmiş Döviz Kurları:**
        * Endpoint: `https://api.freecurrencyapi.com/v1/historical`
        * Kullanım: Seçilen bir döviz kurunun (örn: USD, EUR, GBP) TRY karşısındaki geçmiş günlük değerlerini almak için kullanılır. Uygulama, bu veriyi grafik üzerinde gösterir.
    * **API Anahtarı:** Bu API'yi kullanmak için `YOUR_API_KEY` olarak belirtilen yere FreeCurrencyAPI'den aldığınız kendi API anahtarınızı girmeniz gerekmektedir.

## Veritabanı Yapısı

Uygulama, bilgileri `finances.db` adlı bir SQLite veritabanında saklar. İki ana tablo içerir:

* `assets`: Eklenen varlıkların temel bilgilerini tutar (eklenme tarihi, varlık tipi, miktar, eklendiği andaki kur).
* `transactions`: Varlıklarla ilişkili alım işlemlerini kaydeder (işlem tarihi, miktarı, işlem kuru, maliyet).

## Kurulum

1.  Python 3'ün sisteminizde kurulu olduğundan emin olun.
2.  Gerekli kütüphaneleri yükleyin:
    ```bash
    pip install requests matplotlib
    ```
    (Tkinter genellikle Python standart kütüphanesiyle birlikte gelir.)
3.  Kod içerisindeki API anahtarlarını güncelleyin:
    * `get_currency_rates()` ve `get_gold_rates()` fonksiyonlarındaki `YOUR_API_KEY` yazan yeri CollectAPI anahtarınızla değiştirin.
    * `get_historical_rates()` fonksiyonundaki `YOUR_API_KEY` yazan yeri FreeCurrencyAPI anahtarınızla değiştirin.
4.  Uygulamayı çalıştırın:
    ```bash
    python your_script_name.py
    ```

## Kullanım

1.  **Varlık Ekleme:** Ana ekranda "Miktar" ve "Varlık Tipi" (örn: USD, EUR, GRAM ALTIN) girip "Varlık Ekle" butonuna tıklayın. Varlık, güncel kur üzerinden portföyünüze eklenecektir.
2.  **Güncel Kurları Görüntüleme:** Ana ekranda USD, EUR, GBP için anlık alış/satış kurları listelenir.
3.  **Geçmiş Kur Grafiği:** Ana ekranda döviz cinsi (USD, EUR, GBP) ve periyot (1 Gün, 7 Gün, 30 Gün) seçip "Grafiği Güncelle" butonuna tıklayarak geçmiş kur grafiğini görebilirsiniz.
4.  **Portföy Dağılımı:** Ana ekranın alt kısmında toplam varlık değeriniz ve varlıklarınızın TL cinsinden dağılımını gösteren pasta grafik otomatik olarak güncellenir.
5.  **Geçmiş İşlemler:** "Geçmiş İşlemler" butonuna tıklayarak yeni bir pencere açın. Bu pencerede:
    * Listeden işlem geçmişini görmek istediğiniz varlık tipini seçin.
    * Seçilen varlık tipine ait alım işlemleriniz, alım maliyetleriniz ve anlık kar/zarar durumlarınız listelenecektir.
    * Alt kısımda, seçilen varlığa ait işlemlerin günlük TL değerlerini gösteren bir grafik görüntülenecektir.

---

# Portfolio Management Application (English)

This desktop application allows users to manage their currency and gold assets, track current and historical exchange rate information, and visually monitor the profit/loss status and distribution of their assets.

## Purpose

The primary goal of the application is to provide a user-friendly interface for individual users to easily track their financial portfolios. Users can add different types of assets (Dollar, Euro, Sterling, Gram Gold, etc.), view the current market values of these assets, and analyze their past transactions.

## Features

* **Add Assets:** Different currency types (USD, EUR, GBP) and gold types (Gram Gold, Quarter Gold, etc.) can be added.
* **Current Exchange Rates:** Live buying/selling prices for currencies and gold are listed.
* **Historical Exchange Rate Graphs:** A graph showing the exchange rate changes for a selected currency over the last 1, 7, or 30 days can be displayed.
* **Portfolio Distribution:** The total value of the user's assets in TRY and the distribution by asset type are shown in a pie chart.
* **Past Transactions:**
    * All purchase transactions for a specific asset type are listed.
    * For each transaction, the purchase date, amount, cost at that time (per unit), and days passed are shown.
    * Profit/loss status (percentage and TRY) based on the current rate is calculated for each transaction.
    * Total profit/loss for the selected asset type is displayed.
    * A line graph showing the daily TRY values of transactions for the selected asset type is displayed.
* **Data Storage:** All asset and transaction information is stored in a local SQLite database.
* **User-Friendly Interface:** Developed with the Tkinter library, featuring an easy-to-understand interface.

## Technologies Used

* **Programming Language:** Python 3
* **Interface (GUI):** Tkinter, ttk
* **Data Fetching (API):** requests
* **Database:** SQLite3
* **Graphing:** Matplotlib
* **Date/Time Operations:** datetime

## API Integrations

The application uses the following APIs to fetch current and historical exchange rate information:

1.  **CollectAPI (For Current Rates):**
    * **Currency Rates:**
        * Endpoint: `https://api.collectapi.com/economy/allCurrency`
        * Usage: Used to get current buying and selling prices for popular currencies like USD, EUR, GBP.
    * **Gold Prices:**
        * Endpoint: `https://api.collectapi.com/economy/goldPrice`
        * Usage: Used to get current buying and selling prices for gold types like Gram Gold, Quarter Gold.
    * **API Key:** To use this API, you need to replace `YOUR_API_KEY` with your own API key obtained from CollectAPI.

2.  **FreeCurrencyAPI (For Historical Rates):**
    * **Historical Currency Rates:**
        * Endpoint: `https://api.freecurrencyapi.com/v1/historical`
        * Usage: Used to get historical daily values of a selected currency (e.g., USD, EUR, GBP) against TRY. The application displays this data on a graph.
    * **API Key:** To use this API, you need to replace `YOUR_API_KEY` with your own API key obtained from FreeCurrencyAPI.

## Database Structure

The application stores information in an SQLite database named `finances.db`. It contains two main tables:

* `assets`: Stores basic information about added assets (date added, asset type, amount, rate at the time of addition).
* `transactions`: Records purchase transactions related to assets (transaction date, amount, transaction rate, cost).

## Setup

1.  Ensure Python 3 is installed on your system.
2.  Install the required libraries:
    ```bash
    pip install requests matplotlib
    ```
    (Tkinter usually comes with the Python standard library.)
3.  Update the API keys in the code:
    * Replace `YOUR_API_KEY` in the `get_currency_rates()` and `get_gold_rates()` functions with your CollectAPI key.
    * Replace `YOUR_API_KEY` in the `get_historical_rates()` function with your FreeCurrencyAPI key.
4.  Run the application:
    ```bash
    python your_script_name.py
    ```

## Usage

1.  **Adding Assets:** On the main screen, enter the "Amount" and "Asset Type" (e.g., USD, EUR, GRAM ALTIN) and click the "Varlık Ekle" (Add Asset) button. The asset will be added to your portfolio at the current rate.
2.  **Viewing Current Rates:** Current buying/selling rates for USD, EUR, GBP are listed on the main screen.
3.  **Historical Rate Graph:** On the main screen, select a currency (USD, EUR, GBP) and period (1 Day, 7 Days, 30 Days) and click the "Grafiği Güncelle" (Update Graph) button to see the historical rate graph.
4.  **Portfolio Distribution:** At the bottom of the main screen, a pie chart showing your total asset value and the distribution of your assets in TRY is automatically updated.
5.  **Past Transactions:** Click the "Geçmiş İşlemler" (Past Transactions) button to open a new window. In this window:
    * Select the asset type for which you want to see the transaction history from the list.
    * Your purchase transactions for the selected asset type, your purchase costs, and current profit/loss status will be listed.
    * At the bottom, a graph showing the daily TRY values of transactions for the selected asset will be displayed.
