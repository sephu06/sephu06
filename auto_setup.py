#%%
import os
import pandas as pd
from fuzzywuzzy import fuzz
  # Folder for df
folder1 = "D:\Aadhoc\ActiveMembers"
folder2 = "D:\Aadhoc\Active_EMp_Dump"
if not os.path.exists(folder1):
    raise FileNotFoundError(f"Folder not found: {folder1}")
if not os.path.exists(folder2):
    raise FileNotFoundError(f"Folder not found: {folder2}")

files_in_folder1 = os.listdir(folder1)
files_in_folder2 = os.listdir(folder2)
valid_extensions = ('.csv', '.xlsb', '.xlsx')
files_folder1 = [f for f in files_in_folder1 if f.endswith(valid_extensions)]
files_folder2 = [f for f in files_in_folder2 if f.endswith(valid_extensions)]
print(f"Files in {folder1}: {files_folder1}")
print(f"Files in {folder2}: {files_folder2}")
def read_files_to_df(folder, files):
    dataframes = []
    for file in files:
        file_path = os.path.join(folder, file)
        if file.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file.endswith('.xlsx'):
            df = pd.read_excel(file_path, engine='openpyxl')
        elif file.endswith('.xlsb'):
            df = pd.read_excel(file_path, engine='pyxlsb')
        else:
            continue  # Skip unknown formats
        dataframes.append(df)
    
    # Combine all files into one DataFrame
    return pd.concat(dataframes, ignore_index=True) if dataframes else pd.DataFrame()
df_active_members = read_files_to_df(folder1, files_folder1)
df_active_employees = read_files_to_df(folder2, files_folder2)
df=df_active_members
df1=df_active_employees 
df_PF = df.rename(columns=lambda col: f"{col}_PF")
df1_QP = df1.rename(columns=lambda col: f"{col}_QP")
#######################################
#%%
df_PF.columns
df1_QP['DATE OF BIRTH_QP']
df_PF['DoB_PF']
df_PF['AADHAAR_PF'] = df_PF['AADHAAR_PF'].str.replace(' ', '', regex=False)
df1_QP['DATE OF BIRTH_QP'] = pd.to_numeric(df1_QP['DATE OF BIRTH_QP'], errors='coerce')
df1_QP['DATE OF BIRTH_QP'] = pd.to_datetime(df1_QP['DATE OF BIRTH_QP'], origin='1899-12-30', unit='D')
df1_QP['DATE OF BIRTH_QP']
#######################
df_PF['UAN_PF'] = df_PF['UAN_PF'].astype(str)
df1_QP['UAN_QP'] = df1_QP['UAN_QP'].astype(str)
df_PF['Aadhaar_PF'] = df_PF['AADHAAR_PF'].astype(str)
df1_QP['Aadhaar_QP'] = df1_QP['Aadhar Number_QP'].astype(str)
print("Columns in df:", df.columns)
print("Columns in df1:", df1.columns)

df1_QP['UAN_Last4_QP'] = df1_QP['UAN_QP'].str[-4:].fillna('')
df_PF['UAN_Last4_PF'] = df_PF['UAN_PF'].str[-4:].fillna('')

df1_QP['Aadhaar_Last4_QP'] = df1_QP['Aadhaar_QP'].str[-4:].fillna('')
df_PF['Aadhaar_Last4_PF'] = df_PF['Aadhaar_PF'].str[-4:].fillna('')
print("Columns after extracting last 4 digits:", df1_QP.columns)
matching_uans = df1_QP[df1_QP['UAN_QP'].isin(df_PF['UAN_PF'])]
matching_uans
merged_df = matching_uans.merge(df_PF, 
                                left_on=['UAN_QP', 'UAN_Last4_QP', 'Aadhaar_Last4_QP'],
                                right_on=['UAN_PF', 'UAN_Last4_PF', 'Aadhaar_Last4_PF'],
                                how='inner')
merged_df.columns
filtered_df = merged_df[
    (merged_df['UAN_Last4_QP'] == merged_df['UAN_Last4_PF']) &
    (merged_df['Aadhaar_Last4_QP'] == merged_df['Aadhaar_Last4_PF'])
]

print("Records where UAN and Aadhaar last 4 digits match:")
print(filtered_df[['UAN_QP', 'Aadhaar_PF']])
#merged_df1 = filtered_df.merge(df_PF, on='UAN', suffixes=('_df1', '_df2'))

merged_df.columns
merged_df['Name_PF'] = merged_df['Name_PF'].str.strip()
merged_df['FIRST NAME_QP'] = merged_df['FIRST NAME_QP'].str.strip()
merged_df["Father's/Husband's Name_PF"] = merged_df["Father's/Husband's Name_PF"].str.strip()
merged_df['FATHER NAME_QP'] = merged_df['FATHER NAME_QP'].str.strip()
def check_similarity(name1, name2, threshold=60):
# Converting NaN or None to empty string
    name1 = str(name1) if pd.notna(name1) else ""
    name2 = str(name2) if pd.notna(name2) else ""
    
    similarity_score = fuzz.partial_ratio(name1, name2)

    if similarity_score == 100:
        return "Exact Match"
    elif similarity_score >= threshold:
        return "Partial Match"
    else:
        return "No Match"
merged_df["Status_Name"] = merged_df.apply(lambda row: check_similarity(row["Name_PF"], row["FIRST NAME_QP"]), axis=1)
merged_df["Status_Father_Name"] = merged_df.apply(lambda row: check_similarity(row["FATHER NAME_QP"], row["Father's/Husband's Name_PF"]), axis=1)
merged_df["Status_DoB"] = merged_df.apply(lambda row: "Matched" if row["DoB_PF"] == row["DATE OF BIRTH_QP"] else "Not Matched", axis=1)
merged_df["Status_Gender"] = merged_df.apply(lambda row: "Matched" if row["Gender_PF"] == row["GenderText_QP"] else "Not Matched", axis=1)
merged_df["Status_Aadhar"] = merged_df.apply(lambda row: "Matched" if row["Aadhaar_Last4_PF"] == row["Aadhaar_Last4_QP"] else "Not Matched", axis=1)

mismatch_df = merged_df[
    (merged_df["Status_DoB"] == "Not Matched") |
    (merged_df["Status_Gender"] == "Not Matched") |
    (merged_df["Status_Aadhar"] == "Not Matched")
]
# %%
merged_df
# %%
merged_df