# Copyright (c) 2024, Sanpra Softwares and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document

class PageSheet(Document):
    pass
    # def before_save(self):
    #     lead_id_li = []
    #     leads = frappe.get_all('Lead', fields=['custom_leads_id'])
    #     for lead in leads:
    #         lead_id_li.append(lead.get('custom_leads_id'))

    #     page_sheet_list = frappe.get_all('Page Sheet', ['name'])
    #     for i in page_sheet_list:
    #         page_name, company = frappe.get_value(
    #             "Page Sheet", {'name': i.name}, ["page_name", "company"]
    #         )
    #         sheet_link_doc = frappe.get_value("Sheet Link", {'parent': i.name}, "sheet_link")
            
