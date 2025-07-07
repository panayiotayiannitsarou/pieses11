# app_part2_step1_and_step2_and_step3_and_step4_and_step5.py 

import pandas as pd
import streamlit as st

# --- Βοηθητική: Έλεγχος πλήρως αμοιβαίας φιλίας ---
def is_mutual_friend(df, child1, child2):
    friends1 = str(df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == child1, 'ΦΙΛΟΙ'].values[0]).replace(' ', '').split(',')
    friends2 = str(df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == child2, 'ΦΙΛΟΙ'].values[0]).replace(' ', '').split(',')
    return child2 in friends1 and child1 in friends2

# --- Βήμα 1: Κατανομή Παιδιών Εκπαιδευτικών ---
def assign_teacher_children(df, num_classes):
    teacher_children = df[(df['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] == 'Ν') & (df['ΚΛΕΙΔΩΜΕΝΟΣ'] == False)]
    counts = {f'T{i+1}': 0 for i in range(num_classes)}

    for index, row in teacher_children.iterrows():
        conflicts = str(row['ΣΥΓΚΡΟΥΣΗ']).split(',') if pd.notna(row['ΣΥΓΚΡΟΥΣΗ']) else []
        possible_classes = sorted(counts.items(), key=lambda x: x[1])
        for class_id, _ in possible_classes:
            if df[(df['ΤΜΗΜΑ'] == class_id) & (df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].isin(conflicts))].empty:
                df.at[index, 'ΤΜΗΜΑ'] = class_id
                df.at[index, 'ΚΛΕΙΔΩΜΕΝΟΣ'] = True
                counts[class_id] += 1
                break
    return df

# --- Βήμα 2: Κατανομή Ζωηρών Μαθητών ---
def assign_energetic_students(df, num_classes):
    energetic = df[(df['ΖΩΗΡΟΣ'] == 'Ν') & (df['ΚΛΕΙΔΩΜΕΝΟΣ'] == False)]
    counts = {f'T{i+1}': df[(df['ΤΜΗΜΑ'] == f'T{i+1}') & (df['ΖΩΗΡΟΣ'] == 'Ν')].shape[0] for i in range(num_classes)}

    for index, row in energetic.iterrows():
        conflicts = str(row['ΣΥΓΚΡΟΥΣΗ']).split(',') if pd.notna(row['ΣΥΓΚΡΟΥΣΗ']) else []
        possible_classes = sorted(counts.items(), key=lambda x: x[1])
        for class_id, _ in possible_classes:
            if df[(df['ΤΜΗΜΑ'] == class_id) & (df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].isin(conflicts))].empty:
                df.at[index, 'ΤΜΗΜΑ'] = class_id
                df.at[index, 'ΚΛΕΙΔΩΜΕΝΟΣ'] = True
                counts[class_id] += 1
                break
    return df

# --- Βήμα 3: Κατανομή Παιδιών με Ιδιαιτερότητες ---
def assign_special_needs_students(df, num_classes):
    special_needs = df[(df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν') & (df['ΚΛΕΙΔΩΜΕΝΟΣ'] == False)]
    counts = {f'T{i+1}': df[(df['ΤΜΗΜΑ'] == f'T{i+1}') & (df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν')].shape[0] for i in range(num_classes)}

    for index, row in special_needs.iterrows():
        conflicts = str(row['ΣΥΓΚΡΟΥΣΗ']).split(',') if pd.notna(row['ΣΥΓΚΡΟΥΣΗ']) else []
        possible_classes = sorted(counts.items(), key=lambda x: x[1])
        for class_id, _ in possible_classes:
            if df[(df['ΤΜΗΜΑ'] == class_id) & (df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].isin(conflicts))].empty:
                df.at[index, 'ΤΜΗΜΑ'] = class_id
                df.at[index, 'ΚΛΕΙΔΩΜΕΝΟΣ'] = True
                counts[class_id] += 1
                break
    return df

# --- Βήμα 4: Τοποθέτηση Φίλων Παιδιών των Βημάτων 1–3 ---
def assign_friends_of_locked(df, num_classes):
    locked_students = df[df['ΚΛΕΙΔΩΜΕΝΟΣ'] == True]
    unlocked = df[df['ΚΛΕΙΔΩΜΕΝΟΣ'] == False]

    for index, row in unlocked.iterrows():
        name = row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']
        friends = str(row['ΦΙΛΟΙ']).replace(' ', '').split(',') if pd.notna(row['ΦΙΛΟΙ']) else []
        conflicts = str(row['ΣΥΓΚΡΟΥΣΗ']).split(',') if pd.notna(row['ΣΥΓΚΡΟΥΣΗ']) else []

        for friend in friends:
            if friend in df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].values:
                friend_row = df[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == friend].iloc[0]
                if friend_row['ΚΛΕΙΔΩΜΕΝΟΣ'] == True and is_mutual_friend(df, name, friend):
                    target_class = friend_row['ΤΜΗΜΑ']
                    class_count = df[df['ΤΜΗΜΑ'] == target_class].shape[0]
                    if class_count < 25 and name not in conflicts:
                        if df[(df['ΤΜΗΜΑ'] == target_class) & (df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].isin(conflicts))].empty:
                            df.at[index, 'ΤΜΗΜΑ'] = target_class
                            df.at[index, 'ΚΛΕΙΔΩΜΕΝΟΣ'] = True
                            break

    return df

# --- Βήμα 5: Έλεγχος Ποιοτικών Χαρακτηριστικών ---
def check_characteristics(df):
    characteristics = ['ΦΥΛΟ', 'ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ', 'ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ']
    result = {}
    for class_id in df['ΤΜΗΜΑ'].dropna().unique():
        class_df = df[df['ΤΜΗΜΑ'] == class_id]
        class_stats = {}
        for char in characteristics:
            values = class_df[char].value_counts().to_dict()
            class_stats[char] = values
        result[class_id] = class_stats
    return result

# --- Χρήση στη Streamlit εφαρμογή ---
if 'df' in st.session_state:
    df = st.session_state['df']
    num_classes = st.session_state['num_classes']

    if st.button("🔹 Βήμα 1: Κατανομή Παιδιών Εκπαιδευτικών"):
        df = assign_teacher_children(df, num_classes)
        st.session_state['df'] = df
        st.success("✅ Ολοκληρώθηκε η κατανομή παιδιών εκπαιδευτικών.")
        st.dataframe(df[df['ΚΛΕΙΔΩΜΕΝΟΣ'] == True])

    if st.button("🔹 Βήμα 2: Κατανομή Ζωηρών Μαθητών"):
        df = assign_energetic_students(df, num_classes)
        st.session_state['df'] = df
        st.success("✅ Ολοκληρώθηκε η κατανομή ζωηρών μαθητών.")
        st.dataframe(df[df['ΚΛΕΙΔΩΜΕΝΟΣ'] == True])

    if st.button("🔹 Βήμα 3: Κατανομή Παιδιών με Ιδιαιτερότητες"):
        df = assign_special_needs_students(df, num_classes)
        st.session_state['df'] = df
        st.success("✅ Ολοκληρώθηκε η κατανομή παιδιών με ιδιαιτερότητες.")
        st.dataframe(df[df['ΚΛΕΙΔΩΜΕΝΟΣ'] == True])

    if st.button("🔹 Βήμα 4: Φίλοι Παιδιών των Βημάτων 1–3"):
        df = assign_friends_of_locked(df, num_classes)
        st.session_state['df'] = df
        st.success("✅ Ολοκληρώθηκε η κατανομή φίλων των παιδιών των πρώτων βημάτων.")
        st.dataframe(df[df['ΚΛΕΙΔΩΜΕΝΟΣ'] == True])

    if st.button("🔹 Βήμα 5: Έλεγχος Ποιοτικών Χαρακτηριστικών Τοποθετημένων"):
        stats = check_characteristics(df)
        for class_id, class_stats in stats.items():
            st.subheader(f"📊 Τμήμα {class_id}")
            for char, counts in class_stats.items():
                st.write(f"**{char}**: {counts}")
