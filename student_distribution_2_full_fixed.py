import pandas as pd
import streamlit as st

# --- Βοηθητική: Έλεγχος πλήρως αμοιβαίας φιλίας ---
def is_mutual_friend(df, child1, child2):
    friends1 = str(df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == child1, 'ΦΙΛΟΙ'].values[0]).replace(' ', '').split(',')
    friends2 = str(df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == child2, 'ΦΙΛΟΙ'].values[0]).replace(' ', '').split(',')
    return child2 in friends1 and child1 in friends2

# --- Βήμα 3: Κατανομή Παιδιών με Ιδιαιτερότητες (πλήρης) ---
def assign_special_needs_students(df, class_assignments, num_classes):
    special_needs = df[(df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == 'Ν') & (df['ΤΜΗΜΑ'].isna())]
    class_counts = {i: list(class_assignments[i]) for i in range(num_classes)}
    placed = set()

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

    # --- Υποβήμα 1 ---
    available_students = special_needs[~special_needs['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].isin(placed)].copy()
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
        for class_id in range(num_classes):
            for _, row in available_students.iterrows():
                name = row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']
                if name in placed:
                    continue
                if not has_conflict(name, class_id):
                    class_counts[class_id].append(name)
                    placed.add(name)
                    break

    # --- Υποβήμα 2 ---
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

    # --- Υποβήμα 3 ---
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

    # --- Υποβήμα 4 ---
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
