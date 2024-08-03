import json
import frappe
from frappe.utils import add_to_date, today, date_diff
from datetime import datetime ,timedelta
from frappe import _
from bs4 import BeautifulSoup
from frappe.utils import cstr, now, today
from frappe.auth import LoginManager
from frappe.permissions import has_permission
from frappe.desk.form.assign_to import add,remove
from frappe.utils import (
    cstr,
    get_date_str,
    today,
    nowdate,
    getdate,
    now_datetime,
    get_first_day,
    get_last_day,
    date_diff,
    flt,
    pretty_date,
    fmt_money,
)
from frappe.utils.data import nowtime
from lead_chain.mobile.utils import (
    gen_response,
    generate_key,
    prepare_json_data,
    role_profile,
    ess_validate,
    get_employee_by_user,
    validate_employee_data,
    get_ess_settings,
    get_global_defaults,
    exception_handel,
)

from erpnext.accounts.utils import get_fiscal_year



@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    try:
        login_manager = LoginManager()
        login_manager.authenticate(usr, pwd)
        login_manager.post_login()
        if frappe.response["message"] == "Logged In":
            frappe.response["user"] = login_manager.user
            frappe.response["key_details"] = generate_key(login_manager.user)
        gen_response(200, frappe.response["message"])
    except frappe.AuthenticationError:
        gen_response(500, frappe.response["message"])
    except Exception as e:
        return exception_handel(e)


def validate_employee(user):
    if not frappe.db.exists("Employee", dict(user_id=user)):
        frappe.response["message"] = "Please link Employee with this user"
        raise frappe.AuthenticationError(frappe.response["message"])


@frappe.whitelist()
def get_user_document():
    user_doc = frappe.get_doc("User", frappe.session.user)
    return user_doc


@frappe.whitelist()
def change_password(**kwargs):
    try:
        from frappe.utils.password import check_password, update_password
        data=kwargs
        user = frappe.session.user
        current_password = data.get("current_password")
        new_password = data.get("new_password")
        check_password(user, current_password)
        update_password(user, new_password)
        return gen_response(200, "Password updated")
    except frappe.AuthenticationError:
        return gen_response(500, "Incorrect current password")
    except Exception as e:
        return exception_handel(e)

@frappe.whitelist()
def get_profile():
    try:
        employee_details = frappe.get_cached_value(
            "User",
           frappe.session.user,
            [
                "username",
                "full_name",
                "email",
                "name",
            "time_zone",
                "birth_date",
                "gender",
                "mobile_no"
            ],
            as_dict=True,
        )
        
        image=frappe.get_cached_value(
            "User",frappe.session.user, "user_image",
        )
        if image is not None:
            employee_details["user_image"] = frappe.utils.get_url()+ image
        else:
            employee_details["user_image"] = None
        

        return gen_response(200, "My Profile", employee_details)
    except Exception as e:
        return exception_handel(e)


@frappe.whitelist()
def add_note_in_lead(doc_name, note,activity):
    try:
        doc=frappe.get_doc("Lead",{'name':doc_name},['notes'])
        doc.append("notes", {"note": note,"custom_activity_lead":activity, "added_by": frappe.session.user, "added_on": now()})
        doc.save()

        return gen_response(200, "Note Added Successfully",doc.get('notes'))
    
    except Exception as e:
        return exception_handel(e)

@frappe.whitelist()
def update_profile_picture():
    try:
        from frappe.handler import upload_file
        employee_profile_picture = upload_file()
       
        if employee_profile_picture:
            frappe.db.set_value(
                "User",
                frappe.session.user,
                "user_image",
                employee_profile_picture.file_url,
            )
        return gen_response(200, "Profile picture updated successfully")
    except Exception as e:
        return exception_handel(e)


@frappe.whitelist()
def edit_note_in_lead(doc_name, note, row_id):
    doc=frappe.get_doc("Lead",{'name':doc_name},['notes'])
    for d in doc.notes:
        if cstr(d.name) == row_id:
            d.note = note
            d.db_update()

@frappe.whitelist()
def delete_note_in_lead(doc_name, row_id):
    try:
        doc=frappe.get_doc("Lead",{'name':doc_name},['notes'])
        for d in doc.notes:
            if cstr(d.name) == row_id:
                doc.remove(d)
                break
        doc.save()
        return gen_response(200, "Comment Delete Successfully")
    except Exception as e:
        return exception_handel(e)



from datetime import datetime

def pretty_date(iso_date_str):
    try:
        # Parse ISO 8601 format with timezone
        dt = datetime.fromisoformat(iso_date_str)
        # Format it to a more readable format if needed
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        # Handle parsing errors
        print(f"Error parsing date: {e}")
        return iso_date_str
import json

@frappe.whitelist()
def get_lead(id):
    try:
        if not id:
            return gen_response(500, "Lead id is required")
        if not frappe.db.exists("Lead", id):
            return gen_response(500, "Lead id does not exist")

        lead = frappe.get_doc("Lead", id).as_dict()

        # Retrieve and parse customLeadsdata if it's a JSON field
        if 'custom_leads_data' in lead and lead['custom_leads_data']:
            custom_leads_data = json.loads(lead['custom_leads_data'])
        else:
            custom_leads_data = {}

        # Prepare lead_doc with selected fields
        lead_doc = prepare_json_data(
            [
                "name",
                "first_name",
                "lead_name",
                "lead_owner",
                "created_time",
                "custom_seen_lead",
                "email_id",
                "mobile_no",
                "source",
                "whatsapp_no",
                "territory",
                "custom_sfollow_up",
                "custom_follow_up_datetime",
                "campaign_name",
                # "notes"
            ],
            lead,
        )
        if 'created_time' in custom_leads_data:
            lead_doc['custom_leads_data_created_time'] = pretty_date(custom_leads_data['created_time'])
        # Optionally remove fields from customLeadsdata
        unwanted_fields = [
            "id",
            "ad_id",
            "adset_id",
            "campaign_id",
            "created_time",
            "form_id",
            "is_organic",
            "agree",
            "is_qualified",
            "platform",
            "is_quality",
            "is_converted",
            "@dropdown"
        ]
        for field in unwanted_fields:
            if field in custom_leads_data:
                del custom_leads_data[field]
        custom_leads_data_json = json.dumps(custom_leads_data)
        # assigned_to = frappe.get_all(
        #     "User",
        #     filters=[["User", "email", "in", json.loads(tasks.get("assigned_to"))]],
        #     fields=["full_name as user", "user_image"],
        #     order_by="creation asc",
        # )

        # lead_doc["assigned_to"] = assigned_to
        # Add customLeadsdata as JSON string to lead_doc
        lead_doc['leads_data'] = custom_leads_data_json
        # Optionally fetch and add notes related to customLeadsdata
        # lead_doc["notes"] = get_data_from_notes(id)

        return gen_response(200, "Lead fetched successfully", lead_doc)

    except Exception as e:
        return exception_handel(e)

@frappe.whitelist()
def assignTo(assign_list, name):
    try:

        toDoancel=frappe.db.set_value("ToDo",{"reference_type":"Lead","reference_name":name,"status":"Open"},"status","Cancelled")
        doc = add({
            "assign_to":assign_list,
            "doctype":"Lead",
            "name":name}
        )
        return gen_response(200, "Assigned successfully", doc)
    except Exception as e:
        return exception_handel(e)


@frappe.whitelist()
def get_lead_masters(name):
    try:
        meta_data = {}
        meta_data["notes"] = get_data_from_notes(name)
        meta_data["activity_lead"] = frappe.get_list("Activity Lead", pluck="name")
        meta_data["users"] = frappe.get_list(
            "User",["full_name","name"], order_by="name asc"
        )
        meta_data["whatsapp_sms"]= frappe.db.get_list('whatsapp message', ["message","name"], order_by="creation desc")
        assign_list =frappe.get_list(
            "ToDo", pluck="allocated_to", filters={"reference_type":"Lead","reference_name":name,"status":"open"}
        )
        frappe.msgprint(str(assign_list))
        meta_data["assign_to"] = ", ".join(assign_list) if assign_list else ""
        gen_response(200, "Lead meta data get successfully", meta_data)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted for Lead")
    except Exception as e:
        return exception_handel(e)

@frappe.whitelist()
def get_data_from_notes(doc_name):
    doc = frappe.get_doc("Lead", {'name': doc_name}, ['notes'])
    note_li = []
    for i in doc.notes:
        note_dict = {}

        soup = BeautifulSoup(i.note, 'html.parser')
        paragraphs = soup.find_all('p')
        text_list = [p.get_text(strip=True) for p in paragraphs]

        text_list = list(filter(None, text_list))
        
        # Add formatted message to the note_dict
        note_dict["name"] = int(i.name)
        note_dict["note"] = str(i.note)
        note_dict["commented"] = str(i.added_by)
        note_dict["custom_activity_lead"]=str(i.custom_activity_lead)
        # Check if added_on is not None before formatting
        note_dict["added_on"] = i.added_on.strftime("%Y-%m-%d %H:%M") if i.added_on else None
        str1 = frappe.get_value(
                "User", i.added_by, "user_image", cache=True
            )
        if str1 is not None:
            note_dict['image'] = frappe.utils.get_url()+ str1
        else:
            note_dict['image'] = None
        
        note_li.append(note_dict)

    return note_li



def get_abbreviation(lead_name):
    # Split the name into parts
    parts = lead_name.split()
    # Take the first letter of each part and join them together
    abbreviation = ''.join([part[0].upper() for part in parts])
    return abbreviation

def get_leads(filters):
    try:
        leads = frappe.get_list(
            "Lead",
            fields=[
                "name",
                "owner",
                "lead_name",
                
                "source",
                "custom_page_name",
                "campaign_name",
                "_assign as assigned_to",
            ],
            filters=filters,
            order_by="creation desc"
        )
        
        for lead in leads:
            # Log the fetched lead data
            frappe.logger().info(f"Fetched lead: {lead}")

            # Process the assigned_to field
            assigned_to_json = lead.get("assigned_to")
            if assigned_to_json:
                assigned_to_emails = json.loads(assigned_to_json)
                assigned_to_users = frappe.get_all(
                    "User",
                    filters=[["User", "email", "in", assigned_to_emails]],
                    pluck="full_name",
                    order_by="creation asc",
                )
                assigned_to = ", ".join(assigned_to_users)
            else:
                assigned_to = ""

            lead['abbreviation'] = get_abbreviation(lead.get("lead_name"))
            lead["assigned_to"] = assigned_to
            lead["owner"] = frappe.get_value("User", lead.get("owner"), "full_name")
            lead["custom_seen_lead"]=frappe.get_value("Lead",lead.name,"custom_seen_lead")
        # Log the final leads list before returning
        frappe.logger().info(f"Final leads list: {leads}")

        return leads  # Return the list of leads

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Leads Error")
        return []


# @frappe.whitelist()
# def leadList():
#     try:
#         meta_data={}
#         today = datetime.now().strftime('%Y-%m-%d')
#         meta_data['overdue']=get_leads({'custom_sfollow_up': ['!=', 'Today','Tomorrow','3 Days from Now','1 Week from Now','1 Month from Now','Select Custom Date & Time','Some Day']}) 
#         meta_data['some_day']=get_leads({'custom_sfollow_up': ['=', 'Some Day']})
#         meta_data['today']=get_leads({'custom_sfollow_up': ['=', 'Today']})
#         meta_data['upcoming']=get_leads({'custom_sfollow_up': ['=', 'Tomorrow','3 Days from Now','1 Week from Now','1 Month from Now','Select Custom Date & Time']})
#         gen_response(200, "Lead lists get successfully", meta_data)
#     except frappe.PermissionError:
#         return gen_response(500, "Not permitted for Lead")
#     except Exception as e:
#         return exception_handel(e)
@frappe.whitelist()
def leadList():
    try:
        meta_data={}
        today_start=datetime.now().strftime('%Y-%m-%d 00:00:00')
        today_end=datetime.now().strftime('%Y-%m-%d 23:59:59')

        today_start_datetime = datetime.strptime(today_start, '%Y-%m-%d %H:%M:%S')
        next_day_datetime = today_start_datetime + timedelta(days=1)
        next_day_str = next_day_datetime.strftime('%Y-%m-%d 00:00:00')
        
        meta_data['overdue']= get_leads({'custom_follow_up_datetime': ['<', today_start],'custom_sfollow_up': ['!=', 'Some Day']})
        meta_data['today']=get_leads({'custom_follow_up_datetime': ['between', [today_start,today_end]]}) 
        meta_data['upcoming']=get_leads({'custom_follow_up_datetime': ['>=', next_day_str]})
        meta_data['some_day']=get_leads({'custom_sfollow_up': ['=', 'Some Day']}) 
        gen_response(200, "Lead lists get successfully", meta_data)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted for Lead")
    except Exception as e:
        return exception_handel(e)



@frappe.whitelist()
def cur_current_lead():
    try:
        leads = frappe.get_list(
            "Lead",
            fields=[
                "name",
                "owner",
                "lead_name",
                "source",
                "custom_page_name",
                "campaign_name",
                "_assign as assigned_to",
            ],
            order_by="creation desc"
        )
        for lead in leads:
            assigned_to_json = lead.get("assigned_to")
            if assigned_to_json:
                assigned_to_emails = json.loads(assigned_to_json)
                assigned_to_users = frappe.get_all(
                    "User",
                    filters=[["User", "email", "in", assigned_to_emails]],
                    pluck="full_name",
                    order_by="creation asc",
                )
                # Join the user full names into a single string
                assigned_to = ", ".join(assigned_to_users)
            else:
                assigned_to = ""
            
            lead['abbreviation'] = get_abbreviation(lead.get("lead_name"))
            lead["assigned_to"] = assigned_to
            lead["owner"] = frappe.get_value("User", lead.get("owner"), "full_name")
            lead["custom_seen_lead"]=frappe.get_value("Lead",lead.name,"custom_seen_lead")
        
        return gen_response(200, "Leads list getting Successfully", leads)
    
    except Exception as e:
        return exception_handel(e)








