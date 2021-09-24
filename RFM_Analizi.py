# Hafta 3 - RFM ANALİZİ

# Amaç: Bir e-ticaret şirketi müşterilerinin RFM yöntemiyle segmentlere ayrılıp,
# bu segmentlere göre pazarlama stratejileri belirlenmesidir.

# Buna yönelik olarak müşterilerin davranışlarını tanımlayacağız ve
# bu davranışlarda öbeklenmelere göre gruplar oluşturacağız.
#
# Yani ortak davranışlar sergileyenleri aynı gruplara alacağız ve
# bu gruplara özel satış ve pazarlama teknikleri geliştirmeye çalışacağız.

# Veri Seti Hikayesi

# Online Retail II isimli veri seti İngiltere merkezli online bir satış mağazasının
# 01/12/2009 - 09/12/2011 tarihleri arasındaki satışlarını içeriyor.

# Bu şirket hediyelik eşya satıyor. Promosyon ürünleri gibi düşünebilir.
#
# Müşterilerinin çoğu da toptancı.
#
# Değişkenler
#
# InvoiceNo: Fatura numarası. Her işleme yani faturaya ait eşsiz numara. C ile başlıyorsa iptal edilen işlem.
# StockCode: Ürün kodu. Her bir ürün için eşsiz numara.
# Description: Ürün ismi
# Quantity: Ürün adedi. Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir.
# InvoiceDate: Fatura tarihi ve zamanı.
# UnitPrice: Ürün fiyatı (Sterlin cinsinden)
# CustomerID: Eşsiz müşteri numarası
# Country: Ülke ismi. Müşterinin yaşadığı ülke.

# Bu çalışma "Year2010-2011" verileri için yapılacaktır.

# Görev 1: Veriyi Anlama ve Hazırlama


# 1. Online Retail II excelindeki 2010-2011 verisini okuyunuz. Oluşturduğunuz dataframe’in kopyasını oluşturunuz.

import datetime as dt
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.float_format", lambda x: "%.5f" % x)

df_ = pd.read_excel("C:/Users/Hp/Desktop/DSMLBC6/online_retail_II.xlsx", sheet_name = "Year 2010-2011")

# Orjinal veri setini korumak amacıyla kopyası üzerinden işlem yapacağım.

df = df_.copy()

# 2. Veri setinin betimsel istatistiklerini inceleyiniz.

df.head()
df.columns
df.shape
df.size
df.describe().T

# 3. Veri setinde eksik gözlem var mı? Varsa hangi değişkende kaç tane eksik gözlem vardır?

df.isnull().sum()

# Description (ürün ismi) ve Customer ID (Eşsiz müşteri numaraları) eksik var.

# 4. Eksik gözlemleri veri setinden çıkartınız. Çıkarma işleminde ‘inplace=True’ parametresini kullanınız.

df.dropna(inplace=True)

# 5. Eşsiz ürün sayısı kaçtır?

df["Description"].nunique()

# 6. Hangi üründen kaçar tane vardır?

df["Description"].value_counts()

# 7. En çok sipariş edilen 5 ürünü çoktan aza doğru sıralayınız.

df.groupby("Description").agg({"Quantity": "sum"}).sort_values(by="Quantity", ascending=False).head(5)

# 8. Faturalardaki ‘C’ iptal edilen işlemleri göstermektedir. İptal edilen işlemleri veri setinden çıkartınız.

df = df[~df["Invoice"].str.contains("C", na= False)]

df["Invoice"].value_counts().sum()

# 9. Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluşturunuz.

df["TotalPrice"] = df["Quantity"] * df["Price"]

# Görev 2: RFM metriklerinin hesaplanması

# Recency, Frequency ve Monetary tanımlarını yapınız.

# Recency: Müşterinin kaç gün önce geldiğini ifade eder.
# Frequency: Sıklıktır. Müşterinin kaç adet işlem yaptığını ifade eder.
# Monetary: Müşterinin bıraktığı parasal değerdir.

# Recency için bugünden, son alışveriş yapıldığı tarih çıkarılacaktır.

df["InvoiceDate"].max()

today_date = dt.datetime(2011 , 12, 11)

# Müşteri özelinde Recency, Frequency ve Monetary metriklerini groupby, agg ve lambda ile hesaplayınız.

# Müşterileri RFM yöntemiyle, metriklere göre gruplayacağım.

rfm = df.groupby("Customer ID").agg({"InvoiceDate" : lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     "Invoice" : lambda Invoice: Invoice.nunique(),
                                     "TotalPrice" : lambda TotalPrice : TotalPrice.sum()})

# Oluşturduğunuz metriklerin isimlerini recency, frequency ve monetary olarak değiştiriniz.

rfm.columns = ["recency", "frequency", "monetary"]


rfm = rfm[rfm["monetary"] > 0 ]

# Görev 3: RFM skorlarının oluşturulması ve tek bir değişkene çevrilmesi

# Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çeviriniz.
# Bu skorları recency_score, frequency_score ve monetary_score olarak kaydediniz.

rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels= [5,4,3,2,1])

rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method= "first") ,5 , labels= [1,2,3,4,5])

rfm["recency_monetary"] = pd.qcut(rfm["monetary"], 5, labels= [1,2,3,4,5])

rfm.head()

# Oluşan 2 farklı değişkenin değerini tek bir değişken olarak ifade ediniz ve RFM_SCORE olarak kaydediniz.

rfm["RFM_SCORE"] = (rfm["recency_score"].astype(str)+
                    rfm["frequency_score"].astype(str))

rfm.head()

# Görev 4: RFM skorlarının segment olarak tanımlanması

# Oluşturulan RFM skorların daha açıklanabilir olması için segment tanımlamaları yapınız.

seg_map = { r"[1,2][1,2]" : "hipernating",
            r"[1-2][3-4]" : "at_Risk",
            r"[1-2]5": "cant_loose_them",
            r"3[1-2]": "about_to_sleep",
            r"33": "need_attention",
            r"[3-4][4-5]": "loyal_customers",
            r"41": "promising",
            r"51": "new_customers",
            r"[4-5][2-3]": "potential_loyalists",
            r"5[4-5]": "champions"
            }

# seg_map yardımı ile skorları segmentlere çeviriniz.

rfm["segment"] = rfm["RFM_SCORE"].replace(seg_map, regex =True)

rfm.head()

# Görev 5: Önemli bulduğunuz 3 segmenti seçiniz. Bu üç segmenti;
# -Hem aksiyon kararları açısından,
# -Hem de segmentlerin yapısı açısından (ortalama RFM değerleri) yorumlayınız.


rfm.groupby("segment")["segment", "recency","frequency","monetary"].agg({"mean","count"})


pd.set_option("display.max_columns", None)

rfm[rfm["segment"] == "cant_loose_them"].agg({"mean","max","min"})

# cant_loose_them segmentinin frekansı yüksek ancak müşterinin alışveriş yapması üzerinden çok zaman geçmiş. Bu nedenle
# müşterinin ilgisini çekebilecek fırsatlar, müşteriye özel promosyonlar yapılabilir.

rfm[rfm["segment"] == "need_attention"].agg({"mean","max","min"})

# need_attention segmenti çok arada bir segmenttir. Bu segmentteki müşterilerle ilgilenirse şampiyon müşteriye bile
# dönüşebilirler. Ancak müşteri ile ilgilenilmezse, müşteriyi kaçırma olasılığı da yüksektir. Bu nedenle müşteriyi sürekli
# tetikleyecek, onların ilgisini canlı tutacak reklamlar, indirimler, faaliyetler yapılabilir.


rfm[rfm["segment"] == "potential_loyalists"].agg({"mean","max","min"})

# potential_loyalists segmenti daha yeni müşteridir. Bu müşteriler çok sık gelmezler. Bu nedenle müşterilere mesaj, e-mail
# reklam yoluyla sürekli ürün hatırlatması yapılarak, müşterinin daha sık gelmesi sağlanabilir.

# "Loyal Customers" sınıfına ait customer ID'leri seçerek excel çıktısını alınız.

new_df = pd.DataFrame()
new_df["new_customer_id"] = rfm[rfm["segment"] == "loyal_customers"].index

new_df.to_csv("new_customers.csv")
