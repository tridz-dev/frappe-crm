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

@frappe.whitelist()
def get_conversation_tags(conversation_name):
    """Return tags for a Messenger Conversation as a list of dicts with tag_name and color."""
    doc = frappe.get_doc("Messenger Conversation", conversation_name)
    tags = []
    for row in doc.tags:
        color = frappe.db.get_value("Messenger Tags", row.tag, "color")
        tags.append({"tag_name": row.tag, "color": color})
    return tags
    # return [
    #     {"tag_name": row.tag_name, "color": row.color}
    #     for row in doc.tags
    # ]

@frappe.whitelist()
def set_conversation_tags(conversation_name, tags):
    """Set tags for a Messenger Conversation. Tags is a list of dicts with tag_name and color."""
    import json
    if isinstance(tags, str):
        tags = json.loads(tags)
    doc = frappe.get_doc("Messenger Conversation", conversation_name)
    doc.set("tags", [])
    print("Tags  ==> ",tags)
    for tag in tags:
        doc.append("tags", {
            "tag": tag["tag_name"]
        })
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return True

def on_update(doc, method):
    """Trigger realtime updates when messenger message is updated."""
    try:
        print("Message status update .......", doc.status)
        frappe.publish_realtime(
            "messenger:message_status_update",
            {
                "message_id": doc.message_id,
                "status": doc.status,
                "name":doc.name
            }
        )
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

def on_conversation_update(doc, method):
    """Trigger realtime updates when conversation is updated."""
    try:
        if doc.has_value_changed("block_chat"):
            frappe.publish_realtime(
                "messenger:block_status_update",
                {
                    "conversation_id": doc.name,
                    "blocked": doc.block_chat
                }
            )
        
        if doc.has_value_changed("status"):
            last_status_log = doc.status_log[-1]
            status_log={
                "status": last_status_log.status,
                "changed_on": last_status_log.changed_on,
                "changed_by": last_status_log.changed_by
            }
            frappe.publish_realtime(
                "messenger:conversation_status_update",
                {
                    "conversation_id": doc.name,
                    "status": doc.status,
                    "status_log": status_log
                }
            )
    except Exception as e:
        frappe.log_error("Messenger Conversation Update Error", str(e))

@frappe.whitelist()
def is_helpdesk_ticket_creation_enabled():
    if not frappe.db.exists("DocType", "Messenger Settings"):
        return False
    return frappe.get_cached_value("Messenger Settings", "Messenger Settings", "enable_helpdesk_ticket_creation")

@frappe.whitelist()
def create_helpdesk_ticket_from_messenger(subject, description, conversation_id, ticket_type=None):
    import json
    if isinstance(subject, bytes):
        subject = subject.decode()
    if isinstance(description, bytes):
        description = description.decode()
    if isinstance(conversation_id, bytes):
        conversation_id = conversation_id.decode()
    if isinstance(ticket_type, bytes):
        ticket_type = ticket_type.decode()

    

    # 1. Create the HD Ticket
    ticket_data = {
        "doctype": "HD Ticket",
        "subject": subject,
        "description": description,
        "custom_messenger_conversation": conversation_id
    }
    if ticket_type:
        ticket_data["ticket_type"] = ticket_type
    ticket_doc = frappe.get_doc(ticket_data)
    ticket_doc.insert(ignore_permissions=True)
    ticket_name = ticket_doc.name
    ticket_status = ticket_doc.status if hasattr(ticket_doc, 'status') else "Open"


    # 2. Link to Messenger Conversation (add to hd_tickets child table)
    conversation = frappe.get_doc("Messenger Conversation", conversation_id)
    conversation.latest_ticket_status = ticket_status
    conversation.append("hd_tickets", {
        "hd_ticket": ticket_name,
        "subject": subject,
        "creation_time": ticket_doc.creation,
        "status": ticket_status
    })
    conversation.save(ignore_permissions=True)

    frappe.db.commit()
    return {"ticket": ticket_name, "status": ticket_status}

@frappe.whitelist()
def get_last_tickets_for_conversation(conversation_id, limit=3):
    """
    Return the last N tickets for a Messenger Conversation from the hd_tickets child table.
    Args:
        conversation_id (str): Messenger Conversation name
        limit (int): Number of tickets to return (default 3)
    Returns:
        list of dicts: [{hd_ticket, subject, status, creation_time}]
    """
    doc = frappe.get_doc("Messenger Conversation", conversation_id)
    tickets = sorted(
        [
            {
                "hd_ticket": row.hd_ticket,
                "subject": row.subject,
                "status": row.status,
                "creation_time": row.creation_time,
            }
            for row in doc.hd_tickets
        ],
        key=lambda x: x["creation_time"],
        reverse=True,
    )
    return tickets[: int(limit)]

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