import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import collections
import math

# Postavke stranice
st.set_page_config(page_title="Forenzički AI Dashboard", layout="wide")

st.title("🛡️ Forenzički Dashboard: Detekcija Pranja Novca")

# --- UVODNI DIO ---
with st.expander("ℹ️ Što je Benfordov zakon i kako otkriva kriminal?"):
    st.write("""
    Benfordov zakon kaže da u prirodnim skupovima podataka (poput bankovnih transakcija) 
    brojevi ne počinju svim znamenkama podjednako. Znamenka **1** se pojavljuje u 30% slučajeva, 
    dok znamenka **9** u manje od 5%.
    
    Kada kriminalci ili botovi **umjetno generiraju transakcije** (npr. fiksni iznosi od 500€ ili 50€), 
    oni narušavaju tu prirodnu ravnotežu. Ovaj dashboard vizualizira to odstupanje.
    """)

# --- SIDEBAR: KONTROLE SIMULACIJE ---
st.sidebar.header("Konfiguracija Napada")
broj_transakcija = st.sidebar.slider("Ukupni volumen transakcija", 1000, 50000, 10000)
postotak_prevare = st.sidebar.slider("Udio 'prljavih' transakcija (%)", 0, 50, 15)
sumnjiva_znamenka = st.sidebar.selectbox("Fiksna znamenka bota (Target Digit)", range(1, 10), index=4)

# --- LOGIKA GENERIRANJA PODATAKA ---
@st.cache_data
def generiraj_podatke(n, prevara_posto, znamenka):
    # Legitimne transakcije: log-normalna distribucija (prirodno prati Benforda)
    normalni = np.random.lognormal(mean=5, sigma=2, size=n)
    
    # Generiranje bot-transakcija (Cyber-smurfing)
    n_prevara = int(n * (prevara_posto / 100))
    # Botovi koriste 'ljudske' okrugle brojeve koji počinju s Target Digit
    baza = znamenka * (10**np.random.randint(1, 4, size=n_prevara))
    šum = np.random.uniform(0, 5, size=n_prevara) # minimalno odstupanje da izgledaju slično
    sumnjivi = baza + šum
    
    return np.concatenate([normalni, sumnjivi])

podaci = generiraj_podatke(broj_transakcija, postotak_prevare, sumnjiva_znamenka)

# --- FUNKCIJA ANALIZE ---
def prikaži_analizu(data):
    first_digits = [int(str(abs(int(x)))[0]) for x in data if int(x) != 0]
    counter = collections.Counter(first_digits)
    accum = len(first_digits)
    
    digits = range(1, 10)
    real_freqs = [(counter[d] / accum) * 100 for d in digits]
    expected_freqs = [math.log10(1 + 1/d) * 100 for d in digits]
    
    # 1. Dinamičko objašnjenje trenutne situacije
    st.subheader("Analiza u realnom vremenu")
    if postotak_prevare > 0:
        st.info(f"🔎 **Simulacija napada:** Botovi trenutno ubrizgavaju transakcije koje počinju znamenkom **{sumnjiva_znamenka}**. "
                f"U legitimnom sustavu, ta bi se znamenka trebala pojaviti u **{expected_freqs[sumnjiva_znamenka-1]:.1f}%** slučajeva. "
                f"Trenutno mjerimo **{real_freqs[sumnjiva_znamenka-1]:.1f}%**.")
    else:
        st.success("✨ Sustav trenutno simulira čiste, organske transakcije bez anomalija.")

    # 2. KPI Metrike
    col1, col2, col3 = st.columns(3)
    col1.metric("Obrađeno transakcija", f"{len(data):,}")
    
    anomalije = [str(d) for d in digits if abs(real_freqs[d-1] - expected_freqs[d-1]) > 5]
    col2.metric("Broj detektiranih anomalija", len(anomalije))
    
    status = "RIZIČNO (ALARM)" if anomalije else "SIGURNO"
    col3.metric("Status sustava", status, delta_color="inverse")

    # 3. Vizualni grafikon
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(digits, real_freqs, alpha=0.6, color='crimson', label='Izmjerena frekvencija (Stvarnost)')
    ax.step(digits, expected_freqs, where='mid', color='dodgerblue', label='Teoretska frekvencija (Benford)', linewidth=2.5)
    
    # Isticanje anomalije na grafu
    if str(sumnjiva_znamenka) in anomalije:
        ax.annotate('DETEKTIRANA PREVARA!', xy=(sumnjiva_znamenka, real_freqs[sumnjiva_znamenka-1]), 
                    xytext=(sumnjiva_znamenka+0.5, real_freqs[sumnjiva_znamenka-1]+5),
                    arrowprops=dict(facecolor='black', shrink=0.05), fontsize=12, color='red', fontweight='bold')

    ax.set_xticks(digits)
    ax.set_ylabel("Udio u ukupnom broju (%)")
    ax.set_xlabel("Prva znamenka iznosa")
    ax.legend()
    st.pyplot(fig)

    # 4. Forenzički zaključak (Deep Dive)
    st.markdown("---")
    st.subheader("🕵️ Forenzički zaključak")
    if anomalije:
        st.warning(f"Sustav je automatski izolirao transakcije koje počinju znamenkom **{', '.join(anomalije)}**.")
        st.write(f"""
        **Sljedeći koraci za istražitelja:**
        1. Izolirati sve transakcije čiji iznosi počinju sa **{sumnjiva_znamenka}**.
        2. Provjeriti podudaraju li se vremenski žigovi tih transakcija (botovi često rade u fiksnim razmacima).
        3. Grupirati te transakcije po IP adresama – vjerojatnost je visoka da dolaze iz istog izvora (cyber-smurfing).
        """)
    else:
        st.write("Sve transakcije prate prirodnu logaritamsku distribuciju. Nema indikacija automatiziranog pranja novca.")

# Pokretanje aplikacije
prikaži_analizu(podaci)
