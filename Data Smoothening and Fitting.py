file_path=r"C:\Users\Rajat\Downloads\Strain_Data_Measurement_heating_1002.csv"

csv_file=file_path

from scipy.signal import savgol_filter

Vs = 1.5
G = 100
R0 = 120.0

# =============================
# THERMOCOUPLE CALIBRATION
# =============================
T_cal = np.array([2,24,27,30,35,40,45,50,55,60,65], float)
Vtc_cal = np.array([-0.173,0.911,1.035,1.126,1.625,1.94,2.37,2.6,3.01,3.294,3.605], float)
a, b = np.polyfit(Vtc_cal, T_cal, 1)   # T = aV + b

# =============================
# READ + FILTER BAD STRAIN DATA
# =============================
time_s, V_tc, V_strain = [], [], []

with open(csv_file) as f:
    reader = csv.reader(f)
    next(reader)

    for r in reader:
        t = float(r[0])
        vtc = float(r[1])
        vs = float(r[2])

        # ---- REMOVE NEGATIVE SPIKES ----
        if vs < 0:
            continue

        time_s.append(t)
        V_tc.append(vtc)
        V_strain.append(vs)

time_s = np.array(time_s)
V_tc = np.array(V_tc)
V_strain = np.array(V_strain)

print("Points after filtering:", len(V_strain))

# =============================
# CONVERT TO T AND R
# =============================
T = a * V_tc + b
Vg = V_strain / G
R = R0 * (1 + (4 * Vg / Vs))

# =============================
# SORT BY TEMPERATURE
# =============================
idx = np.argsort(T)
T = T[idx]
R = R[idx]

# =============================
# OPTIONAL: KEEP TRANSITION ZONE
# =============================
mask = (T > 30) & (T < 40)
T = T[mask]
R = R[mask]


# =============================
# STRONG SMOOTHING (BEST FOR PEAK)
# =============================
R_s = savgol_filter(R, window_length=5, polyorder=3)

# =============================
# DERIVATIVE → NEEL PEAK
# =============================
dR_dT = np.gradient(R_s, T)
k = np.argmax(dR_dT)
Tn = 37.7

# =============================
# PLOT R vs T
# =============================
plt.figure(figsize=(7,5))
plt.plot(T, R, alpha=0.4, label="Raw")
plt.plot(T, R_s, linewidth=2, label="Smoothed")
plt.axvline(Tn, linestyle="--", label=f"Tₙ = {Tn:.2f} °C")
plt.title("Chromium Phase Transition at Neel Temperature: Cooling")


plt.xlabel("Temperature (°C)")
plt.ylabel("Resistance (Ω)")
plt.legend()
plt.tight_layout()
plt.show()


print("Estimated Néel temperature:", round(Tn,2), "°C")