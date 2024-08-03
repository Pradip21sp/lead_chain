# import frappe
# import pandas as pd

# def fetch_data_from_sheet(sheet_id):
#     url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
#     try:
#         df = pd.read_csv(url)
#         return df
#     except Exception as e:
#         frappe.log_error(f"Failed to fetch or read data from Google Sheets: {e}", "Lead Import Error")
#         return None

# def conditional_function_camp(campaign_name):
#     return not frappe.db.exists('Campaign', {'campaign_name': campaign_name})

# def conditional_function(lead_id):
#     return not frappe.db.exists('Lead', {'custom_leads_id': lead_id})

# @frappe.whitelist()
# def create_lead_doc():
#     existing_lead_ids = {lead.custom_leads_id for lead in frappe.get_all('Lead', fields=['custom_leads_id'])}
#     campaigns_to_create = set()
#     page_sheet_list = frappe.get_all('Page Sheet', ['name', 'page_name', 'company'])

#     for page_sheet in page_sheet_list:
#         sheet_link_doc = frappe.get_value("Sheet Link", {'parent': page_sheet.name}, "sheet_link")
#         if not sheet_link_doc:
#             continue
        
#         sheet_id = sheet_link_doc.replace("https://docs.google.com/spreadsheets/d/", "").replace("/edit?usp=sharing", "")
#         df = fetch_data_from_sheet(sheet_id)
        
#         if df is None:
#             continue

#         df.columns = df.columns.str.lower().str.replace(' ', '_')

#         for _, row in df.iterrows():
#             lead_id = str(row['id'])
#             if lead_id in existing_lead_ids:
#                 continue

#             if conditional_function_camp(row['campaign_name']):
#                 camp = frappe.new_doc("Campaign")
#                 camp.campaign_name = row['campaign_name']
#                 camp.insert()
            
#             if conditional_function(lead_id):
#                 lead = frappe.new_doc("Lead")
#                 lead.first_name = row['full_name']
#                 lead.lead_name = row['full_name']
#                 lead.status = "Lead"
#                 lead.custom_leads_id = lead_id
#                 lead.source = {
#                     "fb": "Facebook",
#                     "ig": "Instagram"
#                 }.get(row["platform"], "Manual")
#                 lead.email_id = row['email']
#                 lead.mobile_no = str(row['phone_number']).replace("p:", "")
#                 lead.campaign_name = row['campaign_name']
#                 lead.subject = lead_id
#                 lead.custom_page_name = page_sheet.page_name
#                 lead.company = page_sheet.company
#                 lead.custom_leads_data = row.to_json()
#                 lead.save()
                
#                 frappe.log("Lead created", f"Lead for ID {lead_id} created.")
                
#     frappe.msgprint(f"Processing completed. Created Leads for IDs: {', '.join(existing_lead_ids)}")
