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

def get_existing_ids():
    leads = frappe.get_all('Lead', fields=['custom_leads_id'])
    return set(lead.custom_leads_id for lead in leads)

def get_existing_campaigns():
    campaigns = frappe.get_all('Campaign', fields=['campaign_name'])
    return set(campaign.campaign_name for campaign in campaigns)

@frappe.whitelist()
def create_lead_doc():
    lead_id_li = get_existing_ids()
    campaign_name_li = get_existing_campaigns()

    page_sheet_list = frappe.get_all('Page Sheet', ['name', 'page_name', 'company'])

    # Prepare batch lists for bulk insert
    new_campaigns = []
    new_leads = []

    for page_sheet in page_sheet_list:
        sheet_link_doc = frappe.get_value("Sheet Link", {'parent': page_sheet.name}, "sheet_link")
        if not sheet_link_doc:
            continue

        sheet_id = sheet_link_doc.replace("https://docs.google.com/spreadsheets/d/", "").replace("/edit?usp=sharing", "")
        df = fetch_data_from_sheet(sheet_id)

        if df is None:
            continue

        df.columns = df.columns.str.lower().str.replace(' ', '_')

        for _, row in df.iterrows():
            try:
                lead_id = str(row.get('id', '')).strip()
                campaign_name = str(row.get('campaign_name', '')).strip()

                if not lead_id or not campaign_name:
                    continue

                if lead_id in lead_id_li:
                    continue

                if campaign_name not in campaign_name_li:
                    new_campaigns.append({
                        'doctype': 'Campaign',
                        'campaign_name': campaign_name
                    })
                    campaign_name_li.add(campaign_name)
                
                new_leads.append({
                    'doctype': 'Lead',
                    'first_name': row.get('full_name', '').strip(),
                    'lead_name': row.get('full_name', '').strip(),
                    'status': "Lead",
                    'custom_leads_id': lead_id,
                    'source': {
                        "fb": "Facebook",
                        "ig": "Instagram"
                    }.get(row.get("platform", "").strip(), "Manual"),
                    'email_id': row.get('email', '').strip(),
                    'mobile_no': str(row.get('phone_number', '')).replace("p:", "").strip(),
                    'campaign_name': campaign_name,
                    'subject': lead_id,
                    'custom_page_name': page_sheet.page_name,
                    'company': page_sheet.company,
                    'custom_leads_data': row.to_json()
                })

            except Exception as e:
                frappe.log_error(f"Failed to process Lead for ID {row.get('id', '')}: {e}", "Lead Processing Error")

    # Bulk insert new campaigns
    if new_campaigns:
        frappe.get_doc({
            'doctype': 'Campaign',
            'campaigns': new_campaigns
        }).insert(ignore_permissions=True)

    # Bulk insert new leads
    if new_leads:
        for lead_data in new_leads:
            lead = frappe.get_doc(lead_data)
            lead.insert(ignore_permissions=True)

    frappe.msgprint("Processing completed.")




























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

# def conditional_funtion_camp(id):
#     if not frappe.db.sql("""select campaign_name from `tabCampaign` where campaign_name=%s""",id):
#         return True
#     return False


# def conditional_funtion(camp):
#     if not frappe.db.sql("""select custom_leads_id from `tabLead` where custom_leads_id=%s""",camp):
#         return True
#     return False

# @frappe.whitelist()
# def lead_be_save(doc,fn):
#     if not hasattr(frappe.local, 'processed_leads'):
#         frappe.local.processed_leads = False

#     if frappe.local.processed_leads:
#         return
#     frappe.local.processed_leads = True
    
#     # data_get=str(doc.company)+"-"+str(doc.page_name)
#     # frappe.msgprint(data_get)
#     sheetLinkArr=frappe.db.sql("""select sheet_link from `tabSheet Link` where parent=%s""",doc.name)
#     # sheet_id = "1kYb0TDQ0M4cDDTVI9LUZl834eTtnLSmV_klQXkVSYnE"
#     # sheet_id = "1OB-SdDe4SmQyGVHdIjb9grOmiFmV61bxqEc9A4J5RIY"
#     # frappe.msgprint(str(sheetLinkArr))




#     for sheetLink in sheetLinkArr:
#         sheet_id=str(sheetLink[0]).replace("https://docs.google.com/spreadsheets/d/","").replace("/edit?usp=sharing","")
#         df = fetch_data_from_sheet(sheet_id)
#         df = df.rename(columns=str.lower)
#         df.columns = df.columns.str.replace(' ', '_')

#         if df is None:
#             return

#         for index, row in df.iterrows():
#             try:
#                 # frappe.msgprint(str(row))
#                 if conditional_funtion_camp(row['campaign_name']):
#                     camp = frappe.new_doc("Campaign")
#                     camp.campaign_name = row['campaign_name']
#                     camp.insert()
#                 if conditional_funtion(row['id']):
#                     lead = frappe.new_doc("Lead")
#                     lead.first_name = row['full_name']
#                     lead.lead_name = row['full_name']
#                     lead.status = "Lead"
#                     lead.custom_leads_id = row['id']
#                     if row["platform"]=="fb":
#                         lead.source="Facebook"
#                     elif row["platform"]=="ig":
#                         lead.source="Instagram"
#                     else:
#                         lead.source="Manual"
#                     lead.email_id = row['email']
#                     lead.mobile_no = str(row['phone_number']).replace("p:","")
#                     lead.campaign_name =str(row['campaign_name'])
#                     lead.subject = row['id']
#                     lead.custom_page_name=doc.page_name
#                     lead.company = doc.company
#                     lead.custom_leads_data = row.to_json()
#                     # frappe.msgprint(str(lead))
#                     lead.save()

#                     frappe.log("Lead created", f"Lead for ID {row['id']} created.")
#                     break
#             except Exception as e:
#                 frappe.log_error(f"Failed to create Lead for ID {row['id']}: {e}", "Lead Creation Error")
