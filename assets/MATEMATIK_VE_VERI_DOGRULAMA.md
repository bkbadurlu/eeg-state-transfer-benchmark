# Grafik özet: matematik ve sayısal köken denetimi

21 Ekim 2026. Kullanıcının “uydurma şekil olmamalı; uygulanan matematiği
göstermeli” talebi üzerine önceki görsel incelendi ve düzeltildi.

## Önceki şeklin doğru ve eksik tarafları

Yüzey rastgele çizilmiş bir silindir veya torus değildi. Makaledeki katlanmış
yüzeyin (Swiss roll) aynı parametrik denklemiyle çizilmişti. Buna karşılık,
iki farklı kamera görünümü gerçek öğrenilmiş kaynak/hedef eşlemesi değildi;
EEG çizgisi kavramsal bir sinüs bileşimiydi. Bunlar önceki caption'da kavramsal
olarak belirtilmişti; kullanıcının istediği daha sıkı veri/uygulama karşılığını
sağlamak için bu öğeler değiştirildi. Önceki görsel güncel teslim olarak
kullanılmamalıdır; geçmiş sürüm korunmuştur.

## A: uygulanan yüzey ve içsel uzaklık

Makale ve e48_revision_core.py içinde kullanılan denklem:

phi(theta,h) = (theta cos(theta)/10, h, theta sin(theta)/10),
theta in [1.5pi,4.5pi], h in [-1,1].

Bu yüzey için metrik
ds² = (1+theta²)/100 dtheta² + dh².
Arc koordinatı
a(theta) = 0.05 [theta sqrt(1+theta²) + asinh(theta)]
olduğundan (a(theta),h) düzlemindeki uzaklık Öklid uzaklığıdır.

Yeni kalın çizgi, ilk sabit kohortun gerçek ortak probları 0 ve 32 arasında
bu düzlemdeki doğru parçasıdır. a terslenip yüzeye geri taşındı. İçsel doğru
koşulunun sayısal hatası denetim JSON'unda kayıtlıdır. Çizgi, Isomap'ın
geri kazandığı bir yol gibi sunulmaz. Yüzeyin ekrana izdüşümü ortografiktir.

Bu panel bilinen simülasyon üretecini gösterir. İnsan EEG'sinden keşfedilmiş
bir zihinsel yüzey, Riemannian SPD kovaryans manifoldu veya çember koşulu değildir.
Grafik özet yüzey koşulundan seçili bir örnek kullanır; bütün yöntem ve
üreteçlerin tek bir geometrik şekille aynı olduğu iddia edilmez.

## B: gerçek öğrenilmiş temsil ve girdiyle eşleme

Sonuca göre seçim yapmadan ilk orijinal kohort (tohum1800), ilk kaynak6000
ve ilk hedef6003 seçildi. Kayıtlı kod/ayar/tohumlarla yalnız bu iki Isomap
kodlayıcısı ve girdi-yanıt imzasına dayalı afin harita yeniden kuruldu.
Yeni deney koşulu veya derin ağ eğitimi açılmadı.

128 ortak durum probundaki koordinatlar çizildi. Dolu noktalar kaynak,
boş noktalar eşlenmiş hedef koordinatıdır. Tek bir ortak izotropik ölçek
ve ekran ötelemesi kullanıldı; bulutlar ayrı ayrı döndürülmedi, ölçeklenmedi
ve Procrustes ile üst üste getirilmedi. Kesikli çizgi sabit ilk probun
aynı-durum karşılığını gösterir. Durum gerçeği yalnız teşhis eşini bilmek
için kullanıldı; öğrenilmiş haritaya verilmedi.

Yeniden hesaplanan uzaklık rho, koordinat NRMSE ve top5 değerleri mevcut E54
kaydıyla eşleşti. Yani çizimdeki uyumsuzluk da veri karşılığıdır; görsel
olarak başarılı görünmesi için düzeltilmedi.

## C: uygulanan kestirici ve kalibrasyon

Şema artık bilinmeyen gerçek z'yi doğrudan kaynak kestiricisine vermiyor.
H, hizalanmış gözlem temsillerinin geçmişidir; U bilinen girdinin geçmişidir.
Kaynak kestiricisi p = f_s(H,U) üretir.

Kodda hedef raporlarıyla p'den tilde_y - p artıklarına düzenlileştirilmiş
afin bir düzeltme öğrenilir:
yhat_b = p + ehat_b(p), ehat_0=0.

Bu, iki çıktılı simülasyon için matrisli/vektörlü afin düzeltmeyi de kapsar.
Eski a*yhat+b, genel afin fonksiyon ailesini kabaca gösteriyordu; uygulanan
artık parametrizasyonu ve düzenlileştirme önceliğini doğrudan göstermediği
için değiştirildi. Hedef raporları sabit kaynak kestiricisini yeniden eğitmez.
Şekildeki 0/12/48 simülasyon bütçesidir; EEG'de 0/12/32 kullanılmıştır.

## Gerçek EEG ve sayısal sonuçlar

Yapay salınım yerine mevcut kaydedilmiş özellikler kullanıldı: OpenNeuro
ds003061v1.1.2, hedef kişi004, üçüncü kayıt, ilk uygun hedef-ton denemesi
(sıra23), Cz kanalı, 0–200ms içindeki sekiz zaman dilimi ortalaması.
Ham sürekli EEG gibi sunulmaz. Noktalar gerçek saklanmış özellik değerleri,
birleştiren çizgiler düz parçalardır. Zaman konumları 256Hz örnekleme ve
orijinal zaman-dilimi bölmelerinden hesaplanmıştır.

Tek deneme yalnız özellik örneğidir; alttaki RT sonucu bütün önceki 3kaynak/
10hedef analizine aittir. Saat ve işlem kutuları matematiksel/deneysel
işlevi gösteren sembollerdir; yeni ölçüm verisi değildir.

Alt soldaki 0.392/0.168 ve 0.222/0.382 değerleri önceki 20kohort izometrik
sonuçlarından değişmeden alındı. İlk çift denetlenmiş JSON'dan, ikinci çift
mevcut makale tablosundan çekildi. Yeni istatistiksel test yapılmadı.

## Dosyalar ve korunan kayıtlar

GRAPHIC_NUMERIC_INPUTS.npz: çizilen koordinatlar, harita, durumlar, jeodezik,
EEG değerleri/zamanları ve kullanılan ortalamalar.
EVIDENCE_REPLAY_AUDIT.json: sabit seçim kuralı, kaynak hash'leri, eski/yeni
teşhis karşılaştırması ve EEG örneğinin kökeni.
TECHNICAL_FIGURE_PROVENANCE.txt: ayrıntılı İngilizce yöntem/köken açıklaması.
graphical_abstract_caption.txt: kısa İngilizce şekil açıklaması.

Ana TEX/TXT, bilimsel sonuçlar, protokoller, tarihsel103satır ve dört ana
makale şekli değiştirilmedi. LaTeX derlemesi yapılmadı. PDF/SVG özgün vektör
çizimidir; üretken görsel modeli kullanılmadı. Çizim kodunda AI desteği
açıkça kaydedilir; insan yapımı olduğu yönünde yanlış beyan verilmez.
