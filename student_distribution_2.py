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

def assign_special_needs_students(df, class_assignments, num_classes):
    special_needs = df[(df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν') & (df['ΤΜΗΜΑ'].isna())]
    class_counts = {i: list(class_assignments[i]) for i in range(num_classes)}
    placed = set()

    # --- Βοηθητικές ---
    def count_zoiroi(class_id):
        return sum((df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == name, 'ΖΩΗΡΟΣ'] == 'Ν').values[0] for name in class_counts[class_id])

    def count_same_gender(class_id, gender):
        return sum(df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == name, 'ΦΥΛΟ'].values[0] == gender for name in class_counts[class_id])

    def has_conflict(name, class_id):
        conflicts = str(df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == name, 'ΣΥΓΚΡΟΥΣΕΙΣ'].values[0]).replace(" ", "").split(',')
        return any(student in conflicts for student in class_counts[class_id])

    def get_friends(name):
        return str(df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == name, 'ΦΙΛΟΙ'].values[0]).replace(" ", "").split(',')

    def is_mutual_friend(a, b):
        return b in get_friends(a) and a in get_friends(b)

    # --- Υποβήμα 1: Ένας μαθητής με ιδιαιτερότητα ανά τμήμα ---
available_students = special_needs[~special_needs['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].isin(placed)].copy()

# Αν οι μαθητές με ιδιαιτερότητα ≤ αριθμός τμημάτων, βάλε αυστηρά 1 ανά τμήμα
if len(available_students) <= num_classes:
    used_classes = set()
    for _, row in available_students.iterrows():
        name = row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']
        for class_id in range(num_classes):
            if class_id in used_classes:
                continue
            if not has_conflict(name, class_id):
                class_counts[class_id].append(name)
                placed.add(name)
                used_classes.add(class_id)
                break
else:
    # Κανονικά: 1 ανά τμήμα αν γίνεται
    for class_id in range(num_classes):
        for _, row in available_students.iterrows():
            name = row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']
            if name in placed:
                continue
            if not has_conflict(name, class_id):
                class_counts[class_id].append(name)
                placed.add(name)
                break


    # --- Υποβήμα 2: Τοποθέτηση επιπλέον παιδιών με προτεραιότητα λιγότερους ζωηρούς και ισορροπία φύλου ---
    remaining = special_needs[~special_needs['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].isin(placed)]
    for _, row in remaining.iterrows():
        name = row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']
        φύλο = row['ΦΥΛΟ']
        best_class = None
        min_zoiroi = float('inf')
        min_gender_count = float('inf')
        min_total = float('inf')
        for class_id in range(num_classes):
            if has_conflict(name, class_id):
                continue
            zoiroi = count_zoiroi(class_id)
            gender_count = count_same_gender(class_id, φύλο)
            total = len(class_counts[class_id])
            if (
                zoiroi < min_zoiroi or
                (zoiroi == min_zoiroi and gender_count < min_gender_count) or
                (zoiroi == min_zoiroi and gender_count == min_gender_count and total < min_total)
            ):
                best_class = class_id
                min_zoiroi = zoiroi
                min_gender_count = gender_count
                min_total = total
        if best_class is not None:
            class_counts[best_class].append(name)
            placed.add(name)

    # --- Υποβήμα 3: Τοποθέτηση δύο φίλων με ιδιαιτερότητα μαζί (αν επιτρέπεται) ---
    if len(special_needs) > num_classes:
        mutual_pairs = []
        visited = set()
        for _, row1 in special_needs.iterrows():
            name1 = row1['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']
            if name1 in placed or name1 in visited:
                continue
            for _, row2 in special_needs.iterrows():
                name2 = row2['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']
                if name2 in placed or name2 == name1 or name2 in visited:
                    continue
                if is_mutual_friend(name1, name2):
                    mutual_pairs.append((name1, name2))
                    visited.update([name1, name2])
                    break
        for name1, name2 in mutual_pairs:
            for class_id in range(num_classes):
                if (
                    not has_conflict(name1, class_id)
                    and not has_conflict(name2, class_id)
                    and len(class_counts[class_id]) + 2 <= 25
                ):
                    class_counts[class_id].extend([name1, name2])
                    placed.update([name1, name2])
                    break

    # --- Υποβήμα 4: Αν έχουν αμοιβαία φιλία με ήδη τοποθετημένο ζωηρό ή παιδί εκπαιδευτικού ---
    remaining = special_needs[~special_needs['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].isin(placed)]
    for _, row in remaining.iterrows():
        name = row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']
        if name in placed:
            continue
        friends = get_friends(name)
        for friend in friends:
            if friend not in df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].values:
                continue
            if not is_mutual_friend(name, friend):
                continue
            friend_row = df[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == friend].iloc[0]
            if pd.isna(friend_row['ΤΜΗΜΑ']):
                continue
            if friend_row['ΖΩΗΡΟΣ'] != 'Ν' and friend_row['ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ'] != 'Ν':
                continue
            class_id = int(friend_row['ΤΜΗΜΑ']) - 1
            if not has_conflict(name, class_id) and len(class_counts[class_id]) < 25:
                class_counts[class_id].append(name)
                placed.add(name)
                break

    # --- Τελική ενημέρωση στο DataFrame ---
    for class_id, names in class_counts.items():
        for name in names:
            df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == name, 'ΤΜΗΜΑ'] = class_id + 1

    return df

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
