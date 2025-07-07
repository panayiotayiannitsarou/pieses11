
# === Μέρος 1: Ενιαίος Πίνακας Στατιστικών (μόνο Ν/Α) ===

import streamlit as st
import pandas as pd
import math
from io import BytesIO
import matplotlib.pyplot as plt

# ➤ Κλείδωμα με Κωδικό
st.sidebar.title("🔐 Κωδικός Πρόσβασης")
password = st.sidebar.text_input("Εισάγετε τον κωδικό:", type="password")
if password != "katanomi2025":
    st.warning("Παρακαλώ εισάγετε έγκυρο κωδικό για πρόσβαση στην εφαρμογή.")
    st.stop()

# ➤ Ενεργοποίηση/Απενεργοποίηση Εφαρμογής
enable_app = st.sidebar.checkbox("✅ Ενεργοποίηση Εφαρμογής", value=True)
if not enable_app:
    st.info("🔒 Η εφαρμογή είναι προσωρινά απενεργοποιημένη.")
    st.stop()

# ➤ Τίτλος
st.title("🎯 Ψηφιακή Κατανομή Μαθητών – Βήμα 0 με Ενιαίο Πίνακα Στατιστικών")

# ➤ Εισαγωγή Αρχείου Excel
uploaded_file = st.file_uploader("📥 Εισαγωγή Αρχείου Excel Μαθητών", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ Το αρχείο ανέβηκε επιτυχώς!")

    # ➤ Βήμα 0 – Ισορροπία Πληθυσμού
    def calculate_class_distribution(df):
        total_students = len(df)
        max_per_class = 25
        num_classes = math.ceil(total_students / max_per_class)
        st_per_class = total_students // num_classes
        remainder = total_students % num_classes
        class_sizes = [st_per_class + 1 if i < remainder else st_per_class for i in range(num_classes)]
        class_labels = []
        for i, size in enumerate(class_sizes):
            class_labels.extend([f"Τμήμα {i+1}"] * size)
        df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)
        df_shuffled["ΤΜΗΜΑ"] = class_labels
        df_shuffled["ΚΛΕΙΔΩΜΕΝΟΣ"] = False
        return df_shuffled, num_classes

    if st.button("🔄 Κατανομή Μαθητών (Δοκιμαστικό – Βήμα 0)"):
        df, num_classes = calculate_class_distribution(df)
        st.success(f"✅ Η κατανομή ολοκληρώθηκε με {num_classes} τμήματα.")
        st.dataframe(df)

    # ➤ Εξαγωγή σε Excel
    if "ΤΜΗΜΑ" in df.columns:
        output = BytesIO()
        df.to_excel(output, index=False)
        st.download_button("📤 Κατεβάστε το Αποτέλεσμα σε Excel", output.getvalue(), file_name="katanomi_v0.xlsx")

        # ➤ Ενιαίος Πίνακας Στατιστικών
        if st.button("📊 Εμφάνιση Ενιαίου Πίνακα Στατιστικών"):
            st.subheader("📊 Ενιαίος Πίνακας Στατιστικών (μόνο Ν/Α)")

            # Ορισμός κατηγοριών και λογικής φιλτραρίσματος
            categories = {
                "ΦΥΛΟ": ("Α", "Αγόρια (Α)"),
                "ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ": ("Ν", "Παιδιά Εκπαιδευτικών"),
                "ΖΩΗΡΟΣ": ("Ν", "Ζωηροί Μαθητές"),
                "ΙΔΙΑΙΤΕΡΟΤΗΤΑ": ("Ν", "Μαθητές με Ιδιαιτερότητα"),
                "ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ": ("Ν", "Καλή Γνώση Ελληνικών"),
                "ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ": ("Ν", "ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ")
            }

            summary_df = pd.DataFrame()

            for col, (target_val, label) in categories.items():
                if col in df.columns:
                    count_series = df[df[col] == target_val].groupby("ΤΜΗΜΑ")["ΟΝΟΜΑΤΕΠΩΝΥΜΟ"].count()
                    summary_df[label] = count_series

            # Προσθήκη στήλης "Σύνολο Τμήματος"
            summary_df["Σύνολο Τμήματος"] = df.groupby("ΤΜΗΜΑ")["ΟΝΟΜΑΤΕΠΩΝΥΜΟ"].count()

            # Προσθήκη γραμμής "Σύνολο"
            total_row = pd.DataFrame(summary_df.sum(axis=0)).T
            total_row.index = ["Σύνολο"]
            summary_df = pd.concat([summary_df, total_row])
            summary_df = summary_df.fillna(0).astype(int)

            st.dataframe(summary_df)


        # ➤ Ραβδογράμματα Ανά Κατηγορία (Μόνο Ν ή Α)
        if st.button("📈 Εμφάνιση Ραβδογραμμάτων Ανά Κατηγορία"):
            st.subheader("📈 Ραβδογράμματα Κατανομής (Μόνο Ν ή Α Ανά Κατηγορία)")

            categories = {
                "ΦΥΛΟ": ("Α", "Αγόρια (Α)"),
                "ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ": ("Ν", "Παιδιά Εκπαιδευτικών"),
                "ΖΩΗΡΟΣ": ("Ν", "Ζωηροί Μαθητές"),
                "ΙΔΙΑΙΤΕΡΟΤΗΤΑ": ("Ν", "Μαθητές με Ιδιαιτερότητα"),
                "ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ": ("Ν", "Καλή Γνώση Ελληνικών"),
                "ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ": ("Ν", "ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ")
            }

            for col, (target_val, label) in categories.items():
                if col in df.columns:
                    filtered = df[df[col] == target_val]
                    count_series = filtered.groupby("ΤΜΗΜΑ")["ΟΝΟΜΑΤΕΠΩΝΥΜΟ"].count()
                    if not count_series.empty:
                        count_series.plot(kind='bar', title=label)
                        plt.xlabel("Τμήμα")
                        plt.ylabel("Πλήθος Μαθητών")
                        st.pyplot(plt.gcf())
                        plt.clf()
                    else:
                        st.warning(f"⚠️ Δεν υπάρχουν δεδομένα για την κατηγορία: {label}")
                    plt.xlabel("Τμήμα")
                    plt.ylabel("Πλήθος Μαθητών")
                    st.pyplot(plt.gcf())
                    plt.clf()

        # ➤ Ραβδογράμματα Ανά Κατηγορία (Μόνο Ν ή Α)
        if st.button("📈 Εμφάνιση Ραβδογραμμάτων Ανά Κατηγορία", key="bar_chart_alt"):
            st.subheader("📈 Ραβδογράμματα Κατανομής (Μόνο Ν ή Α Ανά Κατηγορία)")

            categories = {
                "ΦΥΛΟ": ("Α", "Αγόρια (Α)"),
                "ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ": ("Ν", "Παιδιά Εκπαιδευτικών"),
                "ΖΩΗΡΟΣ": ("Ν", "Ζωηροί Μαθητές"),
                "ΙΔΙΑΙΤΕΡΟΤΗΤΑ": ("Ν", "Μαθητές με Ιδιαιτερότητα"),
                "ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ": ("Ν", "Καλή Γνώση Ελληνικών"),
                "ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ": ("Ν", "ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ")
            }

            df["ΤΜΗΜΑ"] = df["ΤΜΗΜΑ"].astype(str).str.strip()
            unique_classes = df["ΤΜΗΜΑ"].unique()
            colors = ['#4daf4a', '#377eb8', '#ff7f00', '#984ea3', '#e41a1c', '#a65628']

            for col, (target_val, label) in categories.items():
                if col in df.columns:
                    filtered = df[df[col] == target_val]
                    count_series = filtered.groupby("ΤΜΗΜΑ")["ΟΝΟΜΑΤΕΠΩΝΥΜΟ"].count()
                    count_series = count_series.reindex(unique_classes, fill_value=0)
                    count_series.plot(kind='bar', color=colors[:len(count_series)], title=label)
                    plt.xlabel("Τμήμα")
                    plt.ylabel("Πλήθος Μαθητών")
                    plt.tight_layout()
                    st.pyplot(plt.gcf())
                    plt.clf()
