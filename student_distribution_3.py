# app_part2_step1_and_step2_and_step3_and_step4_and_step5_and_step6_and_step7_and_step8.py 

import pandas as pd
import streamlit as st
import random

# --- Βοηθητική: Έλεγχος πλήρως αμοιβαίας φιλίας ---
def is_mutual_friend(df, child1, child2):
    friends1 = str(df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == child1, 'ΦΙΛΟΙ'].values[0]).replace(' ', '').split(',')
    friends2 = str(df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == child2, 'ΦΙΛΟΙ'].values[0]).replace(' ', '').split(',')
    return child2 in friends1 and child1 in friends2

# [Βήματα 1 έως 6 παραμένουν ίδια...]

# --- Βήμα 7: Υπόλοιποι Μαθητές Χωρίς Φιλίες ---
def assign_remaining_students(df, num_classes):
    remaining = df[(df['ΚΛΕΙΔΩΜΕΝΟΣ'] == False) & (df['ΤΜΗΜΑ'].isna())]
    for index, row in remaining.iterrows():
        name = row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ']
        gender = row['ΦΥΛΟ']
        greek = row['ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ']
        learning = row['ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ']
        conflicts = str(row['ΣΥΓΚΡΟΥΣΗ']).split(',') if pd.notna(row['ΣΥΓΚΡΟΥΣΗ']) else []

        best_class = None
        best_score = float('inf')

        for i in range(num_classes):
            class_id = f'T{i+1}'
            class_df = df[df['ΤΜΗΜΑ'] == class_id]
            if class_df.shape[0] >= 25:
                continue
            if not df[(df['ΤΜΗΜΑ'] == class_id) & (df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].isin(conflicts))].empty:
                continue

            gender_diff = abs(class_df['ΦΥΛΟ'].value_counts().get(gender, 0) - class_df.shape[0] / 2)
            greek_diff = abs(class_df['ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ'].value_counts().get(greek, 0) - class_df.shape[0] / 2)
            learn_diff = abs(class_df['ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ'].value_counts().get(learning, 0) - class_df.shape[0] / 2)
            score = gender_diff + greek_diff + learn_diff

            if score < best_score:
                best_score = score
                best_class = class_id

        if best_class:
            df.at[index, 'ΤΜΗΜΑ'] = best_class
            df.at[index, 'ΚΛΕΙΔΩΜΕΝΟΣ'] = True

    return df

# --- Βήμα 8: Έλεγχος Ποιοτικών Χαρακτηριστικών & Διορθώσεις ---
def balance_qualities(df, num_classes):
    characteristics = ['ΦΥΛΟ', 'ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ', 'ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ']
    for feature in characteristics:
        counts = {f'T{i+1}': df[df['ΤΜΗΜΑ'] == f'T{i+1}'][feature].value_counts() for i in range(num_classes)}
        for val in df[feature].unique():
            class_vals = [(f'T{i+1}', counts[f'T{i+1}'].get(val, 0)) for i in range(num_classes)]
            class_vals.sort(key=lambda x: x[1])
            min_class, min_val = class_vals[0]
            max_class, max_val = class_vals[-1]
            if max_val - min_val > 3:
                swap_from = df[(df['ΤΜΗΜΑ'] == max_class) & (df['ΚΛΕΙΔΩΜΕΝΟΣ'] == False) & (df[feature] == val)]
                swap_to = df[(df['ΤΜΗΜΑ'] == min_class) & (df['ΚΛΕΙΔΩΜΕΝΟΣ'] == False) & (df[feature] != val)]
                for idx_from, row_from in swap_from.iterrows():
                    for idx_to, row_to in swap_to.iterrows():
                        if row_from['ΦΥΛΟ'] == row_to['ΦΥΛΟ']:
                            df.at[idx_from, 'ΤΜΗΜΑ'] = min_class
                            df.at[idx_to, 'ΤΜΗΜΑ'] = max_class
                            break
                    else:
                        continue
                    break
    return df

# --- Χρήση στη Streamlit εφαρμογή ---
if 'df' in st.session_state:
    df = st.session_state['df']
    num_classes = st.session_state['num_classes']

    if st.button("🔹 Βήμα 7: Υπόλοιποι Μαθητές Χωρίς Φιλίες"):
        df = assign_remaining_students(df, num_classes)
        st.session_state['df'] = df
        st.success("✅ Ολοκληρώθηκε η τοποθέτηση των υπολοίπων μαθητών χωρίς φιλίες.")
        st.dataframe(df[df['ΚΛΕΙΔΩΜΕΝΟΣ'] == True])

    if st.button("🔹 Βήμα 8: Έλεγχος Ποιοτικών Χαρακτηριστικών & Διορθώσεις"):
        df = balance_qualities(df, num_classes)
        st.session_state['df'] = df
        st.success("✅ Ολοκληρώθηκε ο έλεγχος και οι διορθώσεις για τα ποιοτικά χαρακτηριστικά.")
        st.dataframe(df)
