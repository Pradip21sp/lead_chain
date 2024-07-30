import frappe
import pandas as pd


def fetch_data_from_sheet(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        frappe.log_error(f"Failed to fetch or read data from Google Sheets: {e}", "Lead Import Error")
        return None

def conditional_funtion_camp(id):
    if not frappe.db.sql("""select campaign_name from `tabCampaign` where campaign_name=%s""",id):
        return True
    return False


def conditional_funtion(camp):
    if not frappe.db.sql("""select custom_leads_id from `tabLead` where custom_leads_id=%s""",camp):
        return True
    return False

def lead_be_save(doc, fn):
    if not hasattr(frappe.local, 'processed_leads'):
        frappe.local.processed_leads = False

    if frappe.local.processed_leads:
        return
    frappe.local.processed_leads = True

    # sheet_id = "1kYb0TDQ0M4cDDTVI9LUZl834eTtnLSmV_klQXkVSYnE"
    sheet_id = "1OB-SdDe4SmQyGVHdIjb9grOmiFmV61bxqEc9A4J5RIY"
    df = fetch_data_from_sheet(sheet_id)
    df = df.rename(columns=str.lower)
    df.columns = df.columns.str.replace(' ', '_')

    if df is None:
        return

    for index, row in df.iterrows():
        try:
            # frappe.msgprint(str(row))
            if conditional_funtion_camp(row['campaign_name']):
                camp = frappe.new_doc("Campaign")
                camp.campaign_name = row['campaign_name']
                camp.insert()
            if conditional_funtion(row['id']):
                lead = frappe.new_doc("Lead")
                lead.first_name = row['full_name']
                lead.lead_name = row['full_name']
                lead.status = "Lead"
                lead.custom_leads_id = row['id']
                if row["platform"]=="fb":
                    lead.source="Facebook"
                elif row["platform"]=="ig":
                    lead.source="Instagram"
                else:
                    lead.source="Manual"
                lead.email_id = row['email']
                lead.mobile_no = str(row['phone_number']).replace("p:","")
                lead.campaign_name =str(row['campaign_name'])
                lead.subject = row['id']
                lead.custom_leads_data = row.to_json()
                lead.save()

                frappe.log("Lead created", f"Lead for ID {row['id']} created.")
                break
        except Exception as e:
            frappe.log_error(f"Failed to create Lead for ID {row['id']}: {e}", "Lead Creation Error")









# import frappe
# import pandas as pd

# def lead_be_save(doc,fn):
#     sheet_id = "1kYb0TDQ0M4cDDTVI9LUZl834eTtnLSmV_klQXkVSYnE"
#     df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv")
    
#     for index, row in df.iterrows():
#             lead = frappe.new_doc("Lead")
#             lead.first_name = f"full name {row['id']}"
#             lead.lead_name = f"full name {row['id']}"
#             lead.status = "Lead"
#             lead.subject = row['id']
#             lead.custom_leads_data = row.to_json()
#             lead.insert()


    # frappe.msgprint(str(doc.custom_leads_data))