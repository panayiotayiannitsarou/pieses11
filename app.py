
# === Μέρος 1: Ενιαίος Πίνακας Στατιστικών (μόνο Ν/Α) ===

import streamlit as st
import pandas as pd
import math
from io import BytesIO

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
st.title("🎯 Ψηφιακή Κατανομή Μαθητών Α΄ Δημοτικού")

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

    if st.button("📌 Τελική Κατανομή Μαθητών (μετά τα 8 Βήματα)"):
        df, num_classes = calculate_class_distribution(df)
        st.session_state["df"] = df
        st.session_state["num_classes"] = num_classes
        st.success(f"✅ Η κατανομή ολοκληρώθηκε με {num_classes} τμήματα.")
        st.subheader("🔍 Προεπισκόπηση Μετά την Κατανομή")
        st.dataframe(df)

    # ➤ Εξαγωγή σε Excel
    if "ΤΜΗΜΑ" in df.columns:
        output = BytesIO()
        df.to_excel(output, index=False)
        st.download_button("📤 Κατεβάστε το Αποτέλεσμα σε Excel", output.getvalue(), file_name="katanomi_v0.xlsx")

        # ➤ Ενιαίος Πίνακας Στατιστικών
        if st.button("📊 Εμφάνιση Ενιαίου Πίνακα Στατιστικών"):
            if "ΤΜΗΜΑ" not in df.columns or df["ΤΜΗΜΑ"].isna().all():
                st.warning("⚠️ Δεν έχει γίνει ακόμη η κατανομή μαθητών. Πρώτα εκτελέστε την κατανομή.")
            else:
                st.subheader("📊 Ενιαίος Πίνακας Στατιστικών (μόνο Ν/Α)")

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

                summary_df["Σύνολο Τμήματος"] = df.groupby("ΤΜΗΜΑ")["ΟΝΟΜΑΤΕΠΩΝΥΜΟ"].count()

                total_row = pd.DataFrame(summary_df.sum(axis=0)).T
                total_row.index = ["Σύνολο"]
                summary_df = pd.concat([summary_df, total_row])
                summary_df = summary_df.fillna(0).astype(int)

                st.dataframe(summary_df)

                st.subheader("🧪 Debug Ανάλυση Χαρακτηριστικών")
                for col, (target_val, label) in categories.items():
                    if col in df.columns:
                        st.markdown(f"**{label}**")
                        filtered = df[df[col] == target_val]
                        st.write(f"Πλήθος με '{target_val}' στο '{col}':", len(filtered))
                        if "ΤΜΗΜΑ" in filtered.columns:
                            st.write("Κατανομή σε ΤΜΗΜΑ:", filtered["ΤΜΗΜΑ"].value_counts())
