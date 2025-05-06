import frappe
from frappe import _

@frappe.whitelist()
def is_messenger_enabled():
    """Check if Messenger is enabled in Messenger Settings."""
    if not frappe.db.exists("DocType", "Messenger Settings"):
        return False
    return frappe.get_cached_value("Messenger Settings", "Messenger Settings", "enabled")

@frappe.whitelist()
def is_messenger_installed():
    """Check if Frappe Messenger app is installed."""
    if not frappe.db.exists("DocType", "Messenger Settings"):
        return False
    return True


def on_update(doc, method):
    """Trigger realtime updates when messenger message is updated."""
    try:
        # Emit conversation update event
        if doc.message_direction == "Outgoing":
            return
        conversation = frappe.get_doc("Messenger Conversation", doc.conversation)
        frappe.publish_realtime(
            "messenger:conversation_update",
            {
                "conversation": conversation.as_dict(),
                "type": "update"
            }
        )
        
        # Emit message update event
        frappe.publish_realtime(
            "messenger:message_update",
            {
                "message": doc.as_dict(),
                "conversation_id": doc.conversation,
                "type": "new"
            }
        )
        
        # Update and emit unread count
        unread_count = frappe.db.count("Messenger Message", {
            "conversation": doc.conversation,
            "message_direction": "Incoming",
            "is_read": 0
        })
        
        frappe.publish_realtime(
            "messenger:unread_update",
            {
                "conversation_id": doc.conversation,
                "unread_count": unread_count
            }
        )
            
    except Exception as e:
        frappe.log_error("Messenger Update Error", str(e))


# def validate(doc, method):
#     """Validate messenger message document before insert."""
#     if doc.type == "Incoming" and doc.get("from"):
#         name, doctype = get_lead_or_deal_from_number(doc.get("from"))
#         doc.reference_doctype = doctype
#         doc.reference_name = name

# def on_update(doc, method):
#     """Trigger realtime updates when messenger message is updated."""
#     frappe.publish_realtime(
#         "messenger_message",
#         {
#             "reference_doctype": doc.reference_doctype,
#             "reference_name": doc.reference_name,
#         },
#     )
#     notify_agent(doc)

# def notify_agent(doc):
#     """Notify assigned agents about new incoming messages."""
#     if doc.type == "Incoming":
#         doctype = doc.reference_doctype
#         if doctype.startswith("CRM "):
#             doctype = doctype[4:].lower()
#         notification_text = f"""
#             <div class="mb-2 leading-5 text-ink-gray-5">
#                 <span class="font-medium text-ink-gray-9">{ _('You') }</span>
#                 <span>{ _('received a messenger message in {0}').format(doctype) }</span>
#                 <span class="font-medium text-ink-gray-9">{ doc.reference_name }</span>
#             </div>
#         """
#         assigned_users = get_assigned_users(doc.reference_doctype, doc.reference_name)
#         for user in assigned_users:
#             notify_user(
#                 {
#                     "owner": doc.owner,
#                     "assigned_to": user,
#                     "notification_type": "Messenger",
#                     "message": doc.message,
#                     "notification_text": notification_text,
#                     "reference_doctype": "Messenger Message",
#                     "reference_docname": doc.name,
#                     "redirect_to_doctype": doc.reference_doctype,
#                     "redirect_to_docname": doc.reference_name,
#                 }
#             )

# def get_lead_or_deal_from_number(number):
#     """Get lead/deal from the given number."""
#     def find_record(doctype, mobile_no, where=""):
#         mobile_no = parse_mobile_no(mobile_no)

#         query = f"""
#             SELECT name, mobile_no
#             FROM `tab{doctype}`
#             WHERE CONCAT('+', REGEXP_REPLACE(mobile_no, '[^0-9]', '')) = {mobile_no}
#         """

#         data = frappe.db.sql(query + where, as_dict=True)
#         return data[0].name if data else None

#     doctype = "CRM Deal"
#     doc = find_record(doctype, number) or None
#     if not doc:
#         doctype = "CRM Lead"
#         doc = find_record(doctype, number, "AND converted is not True")
#         if not doc:
#             doc = find_record(doctype, number)

#     return doc, doctype

# def parse_mobile_no(mobile_no: str):
#     """Parse mobile number to remove spaces, brackets, etc."""
#     return "".join([c for c in mobile_no if c.isdigit() or c == "+"]) 