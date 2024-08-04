# Copyright (c) 2024, Sanpra Softwares and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeMaster(Document):
	def before_save(self):
		if self.password != self.confirm_password:
			frappe.throw("password not matching")

		doc = frappe.new_doc('User')
		doc.first_name= self.first_name
		doc.last_name=self.last_name
		doc.email=self.email   
		doc.mobile_no=self.mobile
		doc.company=self.company
		doc.new_password=self.password
		doc.role_profile_name=self.role
		doc.module_profile="CRM"
		doc.insert(ignore_permissions=True)
		doc.save()	

		# k = frappe.new_doc('User Permission')
		# k.user = self.email
		# k.allow='Company'
		# k.for_value=self.company
		# k.apply_to_all_doctypes =1
		# k.insert()
		# k.save()
	
		frappe.set_value("User",self.email,"role_profile_name",self.role)


	
	
	def on_trash(self):
		frappe.delete_doc("User",self.email,force=True)
		# self.delete_company_name_field_from_user_permission()
		# self.delete_user_name_field_from_user()
	
	# def delete_company_name_field_from_user_permission(self):
	# 	frappe.delete_doc("User Permission",self.doc_user_permission,force=True)

	# def delete_user_name_field_from_user(self):
	# 	frappe.delete_doc("User",self.doc_user,force=True)

