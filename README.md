# 📊 Real-Time Statistical Process Control System for Camera-Controlled Packaging Lines

A Python-based Statistical Process Control (SPC) system for real-time quality monitoring in industrial packaging production lines using camera-based inspection systems.

## 🎯 Overview

This project implements a **Statistical Process Control (SPC)** and alarm system designed for packaging production lines equipped with camera-based quality inspection systems. The system monitors production processes in real-time, detects anomalies, and provides instant alerts based on established control rules.

### Key Features

- ✅ **Real-time Process Monitoring** - Hourly analysis of production and defect data
- 📈 **p-Chart Control Limits** - Automatic calculation of CL, UCL, and LCL
- ⚠️ **Nelson Rules Implementation** - First 4 rules for anomaly detection
- 📊 **Visual Dashboard** - Summary charts showing all production lines
- 🔄 **Stochastic Simulation** - Converts monthly data to hourly simulations
- 🎛️ **Adjustable Variance** - Test different process scenarios (sigma parameter)

## 🏭 Use Case

Designed for packaging facilities with:
- Multiple production lines
- Camera-based quality control systems
- High-volume manufacturing
- Need for proactive quality management

The system is particularly useful for:
- Food packaging
- Pharmaceutical packaging
- FMCG (Fast-Moving Consumer Goods)
- Any high-speed packaging operation

## 📋 Requirements

```bash
Python >= 3.7
numpy >= 1.19.0
matplotlib >= 3.3.0
```

## 🚀 Installation

**Clone the repository**
```bash
git clone https://github.com/bugraozturk-ie/spc-packaging-control.git
cd spc-packaging-control
```

Or install manually:
```bash
pip install numpy matplotlib
```

## 💻 Usage

### Quick Start

```bash
python spc_system_v2.py
```

### Interactive Setup

The program will guide you through:

1. **Sigma Selection** (Process Variation)
   - `0.03` = Under control (low variance) ✅
   - `0.10` = Medium variance
   - `0.20` = High variance
   - `0.30` = Very high variance

2. **Visualization Mode**
   - `1` = Text output only (fast, no graphics)
   - `2` = Summary charts (8 lines in one page)

### Example Session

```
╔════════════════════════════════════════════════════════════════════════╗
║  REAL-TIME SPC SYSTEM FOR CAMERA-CONTROLLED PACKAGING LINES          ║
╚════════════════════════════════════════════════════════════════════════╝

Sigma value (default 0.03): 0.03
Visualization mode (1/2, default 1): 2
✓ Summary charts will be generated.

================================================================================
HOUR: 1
================================================================================

📍 First Exterior
   Production: 1,571 | Defects: 17 | Rate: 0.01082
   ✓ Process under control

📍 First Interior
   Production: 1,867 | Defects: 20 | Rate: 0.01071
   ✓ Process under control

...

📊 Summary chart saved: spc_output_20260208_021807/summary_hour_001.png

▶ Press ENTER to continue, 'q' to quit:
```

## 📊 Production Lines Configuration

The system is pre-configured for 8 production lines:

| Line | Monthly Production | Monthly Defects |
|------|-------------------|-----------------|
| First Exterior | 800,000 | 11,000 |
| First Interior | 950,000 | 10,000 |
| Second Exterior | 800,000 | 11,000 |
| Second Interior | 1,045,000 | 10,000 |
| Third Exterior | 825,000 | 11,000 |
| Third Interior | 2,440,000 | 10,000 |
| Fourth Exterior | 908,000 | 10,000 |
| Fourth Interior | 798,000 | 11,000 |

### Customization

To modify production lines, edit the `PRODUCTION_LINES` dictionary in `spc_system_v2.py`:

```python
PRODUCTION_LINES = {
    'Your Line Name': {
        'monthly_production': 1000000,
        'monthly_defects': 15000
    },
    # Add more lines...
}
```

## 🔍 Technical Details

### Statistical Methods

#### 1. Data Transformation (mhConverter)
Converts monthly aggregated data to hourly simulations:
- **Production**: Normal distribution (μ = monthly avg, σ = user-defined)
- **Defects**: Poisson distribution (λ = expected hourly defects)

#### 2. Control Limits Calculation
p-Chart control limits:
```
CL = p̄ (mean defect rate)
UCL = p̄ + 3√(p̄(1-p̄)/n)
LCL = max(0, p̄ - 3√(p̄(1-p̄)/n))
```

#### 3. Nelson Rules (First 4 Rules)

| Rule | Detection | Description |
|------|-----------|-------------|
| **Rule 1** | Point beyond UCL/LCL | One point outside control limits |
| **Rule 2** | Systematic shift | 7 consecutive points on same side of CL |
| **Rule 3** | Trend | 6 consecutive increasing or decreasing points |
| **Rule 4** | Variance increase | 4 points clustered in outer zone |

### Algorithm Flow

```
1. Initialize control limits (50-hour simulation at σ=0.03)
2. For each hour:
   a. Generate hourly production (Normal distribution)
   b. Generate hourly defects (Poisson distribution)
   c. Calculate failure rate
   d. Apply Nelson rules
   e. Update visualization
   f. Alert if out of control
3. Repeat until user exits
```

## 📁 Project Structure

```
spc-packaging-control/
│
├── spc_system_v2.py          # Main application
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT License
│
└── spc_output_YYYYMMDD_HHMMSS/  # Generated output folder
    ├── summary_hour_001.png
    ├── summary_hour_002.png
    └── ...
```

## 📈 Output

### Text Output
Real-time console display showing:
- Current hour
- Production count per line
- Defect count per line
- Failure rate
- Control status with alerts

### Visual Output (Mode 2)
- PNG files with timestamp
- 4x2 grid showing all 8 production lines
- Color-coded last points (red = alarm, green = normal)
- Control limits clearly marked

## 🎓 Theoretical Background

This system is based on:
- **Shewhart Control Charts** (Walter A. Shewhart, 1931)
- **Western Electric Rules** (1950s)
- **Nelson Rules** (Lloyd S. Nelson, 1984)
- **Statistical Quality Control** (Montgomery, 2020)

### References

1. Montgomery, D. C. (2020). *Introduction to Statistical Quality Control* (8th ed.). Wiley.
2. Nelson, L. S. (1984). The Shewhart control chart—tests for special causes. *Journal of Quality Technology*, 16(4), 237–239.
3. Shewhart, W. A. (1931). *Economic Control of Quality of Manufactured Product*. Van Nostrand.

## 🛠️ Customization & Extension

### Adding More Nelson Rules

Currently implements rules 1-4. To add rules 5-8, extend the `inspection()` function:

```python
def inspection(data, CL, UCL, LCL):
    # ... existing rules ...
    
    # RULE 5: 2 out of 3 points in Zone A or beyond
    if n >= 3:
        # Implementation here
        pass
```

### Integrating Real Data

Replace simulation with real camera system data:

```python
def get_real_data(line_name, hour):
    # Connect to your database/API
    production = fetch_production_count(line_name, hour)
    defects = fetch_defect_count(line_name, hour)
    return production, defects, defects/production
```

### Alternative Control Charts

Extend the system to support:
- **np-chart**: Fixed sample size, defect count
- **c-chart**: Fixed area defect count
- **u-chart**: Defects per unit
- **X̄-R chart**: Variable control

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 👨‍💻 Author

**Buğra Öztürk**
- Industrial Engineering Department
- Manisa Celal Bayar University

## 🙏 Acknowledgments

- Thesis Advisor: Assoc. Prof. Dr. Mehmet Ali Ilgın
- Based on master's thesis: "Development of Real-Time Statistical Process Control and Alarm System for Camera-Controlled Packaging Lines" (June 2025)

## 📞 Support

If you have any questions or need help, please:
- Open an issue on GitHub
- Contact: [bugraozturk.ie@gmail.com]

## 🔮 Future Work

- [ ] Web-based dashboard (Streamlit/Dash)
- [ ] Machine learning anomaly detection
- [ ] Real-time database integration (OPC-UA, MQTT)
- [ ] Multi-language support
- [ ] Email/SMS alert system
- [ ] Historical data analysis tools
- [ ] REST API for external systems

---

⭐ If you find this project useful, please consider giving it a star!

**Made with ❤️ for Quality Engineers**
