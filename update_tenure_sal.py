#%%
##Requirement####
##Adhar,companycode,emp code,offerid,fixed gross,Doj,LWD,Tenure,first sal,last sal,sal_diff
#%%first sal and sal difference based on comp code to f

#%%
import pandas as pd
import warnings
import datetime
import numpy as np
warnings.filterwarnings("ignore")
pd.set_option('display.max_columns', None)
from sqlalchemy import create_engine
#%%
df_employee_data = pd.read_excel('Oct24.xlsb')
df_employee_data['Pay_Period']='2024-10-01'
#%%
df_employee_data1 = pd.read_excel("Nov24.xlsb")
df_employee_data1['Pay_Period']='2024-11-01'
#%%
df_employee_data2 = pd.read_excel("Dec24.xlsb")
df_employee_data2['Pay_Period']='2024-12-01'
#%%
df_employee_data3 = pd.read_excel("Jan25.xlsb")
df_employee_data3['Pay_Period']='2025-01-01'
#%%
df_employee_data4 = pd.read_excel("Feb25.xlsb")
df_employee_data4['Pay_Period']='2025-02-01'
#%%
final_df=pd.concat([df_employee_data,df_employee_data1,df_employee_data2,df_employee_data3,df_employee_data4], ignore_index=True)
# %%
final_df
#%%
final_df.columns
# %%
final_df['offer_count']=final_df.groupby('Aadhar Number')['Deputee_Id'].transform('nunique') 

# %%
final_df=final_df[final_df['offer_count']>1]
final_df
#%%
#df_employee_data['DOJ']=pd.to_datetime(df_employee_data['DATE OF JOINING'], dayfirst=True, errors='coerce')
#df_employee_data['LWD']=pd.to_datetime(df_employee_data['Last_Working_Day'], dayfirst=True, errors='coerce')
#%%

final_df['DATE OF JOINING'] = pd.to_datetime(final_df['DATE OF JOINING'], errors='coerce')
final_df['first__month'] = final_df.groupby('Employee_Code')['DATE OF JOINING'].transform('min').dt.strftime('%B %Y')
final_df['first__month']

#%%
final_df['Last_Working_Day'] = final_df['Last_Working_Day'].fillna('NA')
final_df['Last_Working_Day'] = pd.to_datetime(final_df['Last_Working_Day'], errors='coerce')
final_df['last__month'] = final_df.groupby('Employee_Code')['Last_Working_Day'].transform('min').dt.strftime('%B %Y')
final_df['last__month']

#%%
final_df['first_pay_month']=final_df.groupby('Employee_Code')['Pay_Period'].transform(min)
final_df['first_pay_month']
final_df['last_pay_month']=final_df.groupby('Employee_Code')['Pay_Period'].transform(max)
final_df['last_pay_month']
#%%

final_df['first_pay_sal'] = final_df.loc[
    final_df['Pay_Period'] == final_df['first_pay_month'], 'GROSS'
]
final_df['last_pay_sal'] = final_df.loc[
    final_df['Pay_Period'] == final_df['last_pay_month'], 'GROSS'
]
final_df['first_pay_sal'] = final_df['first_pay_sal'].fillna(0)
final_df['last_pay_sal'] = final_df['last_pay_sal'].fillna(0)


#%%
##########Logic for pay difference####################
####for each adhar number based on doj and lwdd find the first and last pay month and salary
####for each offer id based on adhar and offer id,create column to identify the 1st to n offers
####for pay difference need to find the last pay of previous client and first pay of current client


#%%
date_cols = ['DATE OF JOINING', 'Last_Working_Day']
final_df[date_cols] = final_df[date_cols].apply(pd.to_datetime, dayfirst=True, errors='coerce')
final_df['tenure'] = (final_df['Last_Working_Day'] - final_df['DATE OF JOINING']).dt.days
final_df['tenure']
#final_df.to_csv('data.csv')
# %%
final_df = final_df.sort_values(by=["Employee_Code",'Aadhar Number','Deputee_Id' ,"DATE OF JOINING", "Pay_Period"], ascending=[True, True, True,True,True])
#%%
final_df['last_pay_prev_client'] = final_df.groupby('Aadhar Number')['last_pay_sal'].shift(1)
final_df['first_pay_curr_client'] = final_df['first_pay_sal']
final_df['Pay_Difference'] = final_df['first_pay_curr_client'] - final_df['last_pay_prev_client']


#%%

final_df.to_csv('data1.csv')
#final_df['Pay_Difference']=
# %%
#%%
final_df['Last_Working_Day']

# %%
