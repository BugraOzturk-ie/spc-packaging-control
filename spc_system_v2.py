"""
Kamera Kontrollü Ambalaj Hatları için Gerçek Zamanlı 
İstatistiksel Proses Kontrol ve Alarm Sistemi
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Üretim hatları için aylık veriler
PRODUCTION_LINES = {
    'First Exterior': {'monthly_production': 800000, 'monthly_defects': 11000},
    'First Interior': {'monthly_production': 950000, 'monthly_defects': 10000},
    'Second Exterior': {'monthly_production': 800000, 'monthly_defects': 11000},
    'Second Interior': {'monthly_production': 1045000, 'monthly_defects': 10000},
    'Third Exterior': {'monthly_production': 825000, 'monthly_defects': 11000},
    'Third Interior': {'monthly_production': 2440000, 'monthly_defects': 10000},
    'Fourth Exterior': {'monthly_production': 908000, 'monthly_defects': 10000},
    'Fourth Interior': {'monthly_production': 798000, 'monthly_defects': 11000}
}


def mhConverter(monthly_production, monthly_defects, days=26, shifts=2, hours_per_shift=8, sigma=0.03):
    """
    Aylık üretim verilerini saatlik verilere dönüştürür.
    
    Parameters:
    -----------
    monthly_production : int
        Aylık toplam üretim miktarı
    monthly_defects : int
        Aylık toplam hata sayısı
    days : int
        Aylık çalışma günü sayısı (varsayılan: 26)
    shifts : int
        Günlük vardiya sayısı (varsayılan: 2)
    hours_per_shift : int
        Vardiya başına saat (varsayılan: 8)
    sigma : float
        Varyasyon parametresi (varsayılan: 0.03)
    
    Returns:
    --------
    tuple : (hourly_production, hourly_defects, failure_rate)
    """
    # Toplam çalışma saati
    total_hours = days * shifts * hours_per_shift
    
    # Ortalama saatlik üretim
    avg_hourly_production = monthly_production / total_hours
    
    # Normal dağılımla saatlik üretim simülasyonu
    hourly_production = int(np.random.normal(
        loc=avg_hourly_production,
        scale=avg_hourly_production * sigma
    ))
    
    # Hata oranı
    defect_rate = monthly_defects / monthly_production
    
    # Beklenen saatlik hata sayısı
    expected_hourly_defects = defect_rate * hourly_production
    
    # Poisson dağılımı ile saatlik hata simülasyonu
    hourly_defects = np.random.poisson(lam=expected_hourly_defects)
    
    # Saatlik hata oranı
    failure_rate = hourly_defects / hourly_production if hourly_production > 0 else 0
    
    return hourly_production, hourly_defects, failure_rate


def calculate_control_limits(failure_rates, production_counts):
    """
    p-chart kontrol limitlerini hesaplar.
    
    Parameters:
    -----------
    failure_rates : list
        Hata oranları listesi
    production_counts : list
        Üretim miktarları listesi
    
    Returns:
    --------
    tuple : (CL, UCL, LCL)
    """
    # Merkez çizgi (ortalama hata oranı)
    CL = np.mean(failure_rates)
    
    # Ortalama üretim miktarı
    avg_n = np.mean(production_counts)
    
    # Standart sapma
    std_dev = np.sqrt(CL * (1 - CL) / avg_n)
    
    # Üst ve alt kontrol limitleri (±3 sigma)
    UCL = CL + 3 * std_dev
    LCL = CL - 3 * std_dev
    
    # LCL negatif olamaz
    LCL = max(0, LCL)
    
    return CL, UCL, LCL


def inspection(data, CL, UCL, LCL):
    """
    Nelson kurallarına dayalı kontrol dışı durum analizi.
    İlk 4 Nelson kuralını uygular.
    
    Parameters:
    -----------
    data : list
        Hata oranları listesi
    CL : float
        Merkez çizgi
    UCL : float
        Üst kontrol limiti
    LCL : float
        Alt kontrol limiti
    
    Returns:
    --------
    list : Tespit edilen durumlar
    """
    comments = []
    n = len(data)
    
    if n == 0:
        return comments
    
    # KURAL 1: Son nokta UCL veya LCL dışında mı?
    if data[-1] > UCL or data[-1] < LCL:
        comments.append("⚠️ KURAL 1: Kontrol dışı nokta tespit edildi! (UCL/LCL aşıldı)")
    
    # KURAL 2: Son 7 nokta CL'nin aynı tarafında mı?
    if n >= 7:
        last_7 = data[-7:]
        above_cl = all(x > CL for x in last_7)
        below_cl = all(x < CL for x in last_7)
        
        if above_cl or below_cl:
            comments.append("⚠️ KURAL 2: Sistematik kayma tespit edildi! (7 ardışık nokta CL'nin aynı tarafında)")
    
    # KURAL 3: Art arda 6 artan veya azalan nokta var mı?
    if n >= 6:
        last_6 = data[-6:]
        increasing = all(last_6[i] < last_6[i+1] for i in range(5))
        decreasing = all(last_6[i] > last_6[i+1] for i in range(5))
        
        if increasing:
            comments.append("⚠️ KURAL 3: Artan trend tespit edildi! (6 ardışık artan nokta)")
        elif decreasing:
            comments.append("⚠️ KURAL 3: Azalan trend tespit edildi! (6 ardışık azalan nokta)")
    
    # KURAL 4: Son 4 nokta CL ile UCL (veya LCL) arasında uçta mı?
    if n >= 4:
        last_4 = data[-4:]
        upper_zone = all(x > CL and x < UCL for x in last_4)
        # CL ile UCL arası orta noktası
        mid_upper = CL + (UCL - CL) * 2/3
        
        upper_extreme = all(x > mid_upper for x in last_4)
        
        if upper_extreme and upper_zone:
            comments.append("⚠️ KURAL 4: Varyans artışı olabilir! (4 nokta uçta kümelenmiş)")
    
    if not comments:
        comments.append("✓ Süreç kontrol altında")
    
    return comments


def create_summary_chart(all_hourly_data, control_limits, current_hour, output_dir):
    """
    Tüm hatlar için özet grafik oluşturur.
    
    Parameters:
    -----------
    all_hourly_data : dict
        Tüm hatların saatlik verileri
    control_limits : dict
        Tüm hatların kontrol limitleri
    current_hour : int
        Mevcut saat
    output_dir : str
        Çıktı dizini
    """
    fig, axes = plt.subplots(4, 2, figsize=(16, 12))
    fig.suptitle(f'Tüm Hatlar - p-Chart Özeti (Saat: {current_hour})', fontsize=16, fontweight='bold')
    
    lines = list(PRODUCTION_LINES.keys())
    
    for idx, (ax, line_name) in enumerate(zip(axes.flat, lines)):
        data = all_hourly_data[line_name]
        limits = control_limits[line_name]
        
        # Grafik çiz
        ax.plot(data['hours'], data['rates'], marker='o', linestyle='-', 
                color='black', markersize=4, linewidth=1.5)
        
        # Kontrol limitleri
        ax.axhline(y=limits['CL'], color='blue', linestyle='--', linewidth=1.5, alpha=0.7)
        ax.axhline(y=limits['UCL'], color='red', linestyle='--', linewidth=1.5, alpha=0.7)
        ax.axhline(y=limits['LCL'], color='red', linestyle='--', linewidth=1.5, alpha=0.7)
        
        # Son noktayı vurgula
        if len(data['rates']) > 0:
            last_rate = data['rates'][-1]
            color = 'red' if (last_rate > limits['UCL'] or last_rate < limits['LCL']) else 'green'
            ax.plot(data['hours'][-1], last_rate, 'o', color=color, markersize=8, zorder=5)
        
        ax.set_title(line_name, fontsize=10, fontweight='bold')
        ax.set_xlabel('Saat', fontsize=8)
        ax.set_ylabel('Hata Oranı', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.tick_params(labelsize=8)
    
    plt.tight_layout()
    filename = os.path.join(output_dir, f'summary_hour_{current_hour:03d}.png')
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    
    return filename


def initialize_control_limits(line_name, line_data, sigma=0.03):
    """
    Her hat için kontrol limitlerini başlangıçta hesaplar.
    50 saatlik simülasyon ile CL, UCL, LCL belirler.
    
    Parameters:
    -----------
    line_name : str
        Hat adı
    line_data : dict
        Hat verileri (monthly_production, monthly_defects)
    sigma : float
        Varyasyon parametresi
    
    Returns:
    --------
    tuple : (CL, UCL, LCL)
    """
    failure_rates = []
    production_counts = []
    
    # 50 saatlik veri üret
    for _ in range(50):
        prod, defects, rate = mhConverter(
            line_data['monthly_production'],
            line_data['monthly_defects'],
            sigma=sigma
        )
        failure_rates.append(rate)
        production_counts.append(prod)
    
    # Kontrol limitlerini hesapla
    CL, UCL, LCL = calculate_control_limits(failure_rates, production_counts)
    
    return CL, UCL, LCL


def run_simulation(sigma=0.03, mode='text'):
    """
    Ana simülasyon döngüsü.
    
    Parameters:
    -----------
    sigma : float
        Varyasyon parametresi (0.03 = kontrol altında, daha yüksek = varyans artışı)
    mode : str
        'text' = sadece metin, 'summary' = özet grafik, 'detailed' = her hat için ayrı grafik
    """
    print("=" * 80)
    print("SPC SİMÜLASYONU BAŞLADI")
    print("=" * 80)
    print(f"Varyasyon Parametresi (Sigma): {sigma}")
    print(f"Mod: {mode}")
    print("=" * 80)
    
    # Çıktı dizini oluştur
    if mode != 'text':
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"spc_output_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        print(f"\n📁 Grafikler kaydedilecek: {output_dir}/")
    
    # Tüm hatlar için kontrol limitlerini başlangıçta hesapla
    control_limits = {}
    print("\n📊 Kontrol limitleri hesaplanıyor...\n")
    
    for line_name, line_data in PRODUCTION_LINES.items():
        CL, UCL, LCL = initialize_control_limits(line_name, line_data, sigma=0.03)
        control_limits[line_name] = {'CL': CL, 'UCL': UCL, 'LCL': LCL}
        print(f"{line_name:20s} | CL: {CL:.5f} | UCL: {UCL:.5f} | LCL: {LCL:.5f}")
    
    print("\n" + "=" * 80)
    print("Kontrol limitleri hazır. Simülasyon başlatılıyor...")
    print("Devam etmek için ENTER, çıkmak için 'q' yazın.")
    print("=" * 80 + "\n")
    
    # Saatlik veriler için hafıza
    hourly_data = {line: {'hours': [], 'rates': [], 'productions': []} 
                   for line in PRODUCTION_LINES.keys()}
    
    current_hour = 1
    
    while True:
        print(f"\n{'='*80}")
        print(f"SAAT: {current_hour}")
        print(f"{'='*80}\n")
        
        # Her hat için saatlik veri üret ve analiz et
        for line_name, line_data in PRODUCTION_LINES.items():
            limits = control_limits[line_name]
            
            # Saatlik veri üret
            prod, defects, rate = mhConverter(
                line_data['monthly_production'],
                line_data['monthly_defects'],
                sigma=sigma
            )
            
            # Hafızaya ekle
            hourly_data[line_name]['hours'].append(current_hour)
            hourly_data[line_name]['rates'].append(rate)
            hourly_data[line_name]['productions'].append(prod)
            
            # Kontrol analizi
            comments = inspection(
                hourly_data[line_name]['rates'],
                limits['CL'],
                limits['UCL'],
                limits['LCL']
            )
            
            # Sonuçları yazdır
            print(f"📍 {line_name}")
            print(f"   Üretim: {prod:,} | Hata: {defects} | Oran: {rate:.5f}")
            for comment in comments:
                print(f"   {comment}")
            print()
        
        # Grafik oluştur
        if mode == 'summary':
            filename = create_summary_chart(hourly_data, control_limits, current_hour, output_dir)
            print(f"📊 Özet grafik kaydedildi: {filename}\n")
        
        # Kullanıcı girişi
        user_input = input("\n▶ Devam için ENTER, çıkış için 'q': ").strip().lower()
        
        if user_input == 'q':
            print("\n" + "="*80)
            print("Simülasyon sonlandırıldı.")
            print(f"Toplam {current_hour} saat simüle edildi.")
            if mode != 'text':
                print(f"Grafikler kaydedildi: {output_dir}/")
            print("="*80)
            break
        
        current_hour += 1


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════════════╗
    ║  KAMERA KONTROLLÜ AMBALAJ HATLARI İÇİN                                ║
    ║  GERÇEK ZAMANLI İSTATİSTİKSEL PROSES KONTROL VE ALARM SİSTEMİ        ║
    ╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    print("\n1. Sigma değeri seçin:")
    print("  0.03 = Kontrol altında (düşük varyans)")
    print("  0.10 = Orta seviye varyans")
    print("  0.20 = Yüksek varyans")
    print("  0.30 = Çok yüksek varyans")
    
    try:
        sigma_input = input("\nSigma değeri (varsayılan 0.03): ").strip()
        sigma = float(sigma_input) if sigma_input else 0.03
    except:
        sigma = 0.03
        print("Geçersiz giriş, varsayılan değer (0.03) kullanılıyor.")
    
    print("\n2. Görselleştirme modu seçin:")
    print("  1 = Sadece metin çıktısı (hızlı)")
    print("  2 = Özet grafik (8 hat tek sayfada)")
    
    try:
        mode_input = input("\nMod seçimi (1/2, varsayılan 1): ").strip()
        if mode_input == '2':
            mode = 'summary'
            print("✓ Özet grafikler oluşturulacak.")
        else:
            mode = 'text'
            print("✓ Sadece metin çıktısı kullanılacak.")
    except:
        mode = 'text'
    
    print("\n" + "="*80)
    input("Başlamak için ENTER'a basın...")
    print()
    
    run_simulation(sigma=sigma, mode=mode)
