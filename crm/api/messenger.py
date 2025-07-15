import frappe
from frappe import _


@frappe.whitelist()
def is_messenger_enabled():
    """Check if Messenger is enabled in Messenger Settings."""
    if not frappe.db.exists("DocType", "Messenger Settings"):
        return False
    return frappe.get_cached_value(
        "Messenger Settings", "Messenger Settings", "enabled"
    )


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
    print("Tags  ==> ", tags)
    for tag in tags:
        doc.append("tags", {"tag": tag["tag_name"]})
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return True


def on_update(doc, method):
    """Trigger realtime updates when messenger message is updated."""
    try:
        frappe.publish_realtime(
            "messenger:message_status_update",
            {"message_id": doc.message_id, "status": doc.status, "name": doc.name},
        )

        # Handle outgoing messages - emit message_sent event for sidebar updates
        if doc.message_direction == "Outgoing":
            frappe.publish_realtime(
                "messenger:message_sent",
                {"conversation_id": doc.conversation, "message": doc.as_dict()},
            )

            # Also emit conversation update for sidebar
            conversation = frappe.get_doc("Messenger Conversation", doc.conversation)
            frappe.publish_realtime(
                "messenger:conversation_update",
                {"conversation": conversation.as_dict(), "type": "update"},
            )
             # Handle auto-generated outgoing messages
            if (
                doc.is_auto_generated_outgoing_message == 1
                and doc.status == "sent"
            ):
                frappe.publish_realtime(
                    "messenger:message_auto_sent",
                    {
                        "message": doc.as_dict(),
                        "conversation_id": doc.conversation,
                        "type": "new",
                    },
                )
            return

        # Handle incoming messages
        if doc.message_direction == "Incoming":
            # Emit conversation update event
            attachment_content_types = ["file", "image", "video", "audio", "document"]
            if doc.content_type in attachment_content_types:
                if not doc.attach:
                    return
            conversation = frappe.get_doc("Messenger Conversation", doc.conversation)
            frappe.publish_realtime(
                "messenger:conversation_update",
                {"conversation": conversation.as_dict(), "type": "update"},
            )

            # Emit message update event
            frappe.publish_realtime(
                "messenger:message_update",
                {
                    "message": doc.as_dict(),
                    "conversation_id": doc.conversation,
                    "type": "new",
                },
            )

            # Update and emit unread count
            unread_count = frappe.db.count(
                "Messenger Message",
                {
                    "conversation": doc.conversation,
                    "message_direction": "Incoming",
                    "is_read": 0,
                },
            )

            frappe.publish_realtime(
                "messenger:unread_update",
                {"conversation_id": doc.conversation, "unread_count": unread_count},
            )

       

    except Exception as e:
        frappe.log_error("Messenger Update Error", str(e))


def on_conversation_update(doc, method):
    """Trigger realtime updates when conversation is updated."""
    try:
        if doc.has_value_changed("block_chat"):
            frappe.publish_realtime(
                "messenger:block_status_update",
                {"conversation_id": doc.name, "blocked": doc.block_chat},
            )

        if doc.has_value_changed("status"):
            last_status_log = doc.status_log[-1]
            status_log = {
                "status": last_status_log.status,
                "changed_on": last_status_log.changed_on,
                "changed_by": last_status_log.changed_by,
            }
            frappe.publish_realtime(
                "messenger:conversation_status_update",
                {
                    "conversation_id": doc.name,
                    "status": doc.status,
                    "status_log": status_log,
                },
            )
    except Exception as e:
        frappe.log_error("Messenger Conversation Update Error", str(e))


@frappe.whitelist()
def is_helpdesk_ticket_creation_enabled():
    if not frappe.db.exists("DocType", "Messenger Settings"):
        return False
    return frappe.get_cached_value(
        "Messenger Settings", "Messenger Settings", "enable_helpdesk_ticket_creation"
    )


@frappe.whitelist()
def create_helpdesk_ticket_from_messenger(
    subject, description, conversation_id, ticket_type=None
):
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
        "custom_messenger_conversation": conversation_id,
    }
    if ticket_type:
        ticket_data["ticket_type"] = ticket_type
    ticket_doc = frappe.get_doc(ticket_data)
    ticket_doc.insert(ignore_permissions=True)
    ticket_name = ticket_doc.name
    ticket_status = ticket_doc.status if hasattr(ticket_doc, "status") else "Open"

    # 2. Link to Messenger Conversation (add to hd_tickets child table)
    conversation = frappe.get_doc("Messenger Conversation", conversation_id)
    conversation.latest_ticket_status = ticket_status
    conversation.append(
        "hd_tickets",
        {
            "hd_ticket": ticket_name,
            "subject": subject,
            "creation_time": ticket_doc.creation,
            "status": ticket_status,
        },
    )
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


@frappe.whitelist()
def get_conversation_details(conversation_id, limit=20, before=None):
    """Get all conversation details in a single API call for better performance, with support for infinite scroll."""
    try:
        # Get conversation details
        conversation = frappe.get_doc("Messenger Conversation", conversation_id)

        # Prepare message filters
        message_filters = {"conversation": conversation_id}
        if before:
            message_filters["timestamp"] = ["<", before]

        # Get messages (latest 'limit', older than 'before' if provided)
        messages = frappe.get_all(
            "Messenger Message",
            filters=message_filters,
            fields=[
                "name",
                "message",
                "sender_id",
                "sender_user",
                "timestamp",
                "message_direction",
                "conversation",
                "is_read",
                "content_type",
                "attach",
                "status",
            ],
            order_by="timestamp desc",
            limit=int(limit),
        )

        # Get conversation tags
        tags = []
        for row in conversation.tags:
            color = frappe.db.get_value("Messenger Tags", row.tag, "color")
            tags.append({"tag_name": row.tag, "color": color})

        # Get assignees
        assignees = []
        todos = frappe.get_all(
            "ToDo",
            filters=[
                ["reference_type", "=", "Messenger Conversation"],
                ["reference_name", "=", conversation_id],
                ["status", "=", "Open"],
            ],
            fields=["allocated_to"],
        )

        if todos:
            user_ids = [todo.allocated_to for todo in todos]
            users = frappe.get_all(
                "User",
                filters=[["name", "in", user_ids]],
                fields=["name", "full_name", "user_image"],
            )
            user_map = {user.name: user for user in users}
            assignees = [
                {
                    "name": todo.allocated_to,
                    "image": user_map.get(todo.allocated_to, {}).get("user_image"),
                    "label": user_map.get(todo.allocated_to, {}).get("full_name")
                    or todo.allocated_to,
                }
                for todo in todos
            ]

        # Get status updates
        status_updates = []
        if conversation.status_log:
            for log in conversation.status_log:
                status_updates.append(
                    {
                        "status": log.status,
                        "changed_on": log.changed_on,
                        "changed_by": log.changed_by,
                    }
                )

        # Get past tickets
        past_tickets = []
        if hasattr(conversation, "hd_tickets") and conversation.hd_tickets:
            tickets = sorted(
                [
                    {
                        "hd_ticket": row.hd_ticket,
                        "subject": row.subject,
                        "status": row.status,
                        "creation_time": row.creation_time,
                    }
                    for row in conversation.hd_tickets
                ],
                key=lambda x: x["creation_time"],
                reverse=True,
            )
            past_tickets = tickets[:3]

        # Get unread count
        unread_count = frappe.db.count(
            "Messenger Message",
            {
                "conversation": conversation_id,
                "message_direction": "Incoming",
                "is_read": 0,
            },
        )

        return {
            "conversation": conversation.as_dict(),
            "messages": messages,
            "tags": tags,
            "assignees": assignees,
            "status_updates": status_updates,
            "past_tickets": past_tickets,
            "unread_count": unread_count,
        }

    except Exception as e:
        frappe.log_error("Get Conversation Details Error", str(e))
        return None


@frappe.whitelist()
def get_conversations_with_details(
    limit=20, offset=0, platform_filter=None, filters=None
):
    """Get conversations with all details in a single API call for better performance, supporting all filter operators from frontend."""
    try:
        base_filters = [["block_chat", "=", 0]]
        if platform_filter and platform_filter != "all":
            base_filters.append(["platform", "=", platform_filter])
        import json

        if filters:
            if isinstance(filters, str):
                filters = json.loads(filters)
            if isinstance(filters, dict):
                for k, v in filters.items():
                    if isinstance(v, list) and len(v) == 2:
                        base_filters.append([k, v[0], v[1]])
                    else:
                        base_filters.append([k, "=", v])
            elif isinstance(filters, list):
                base_filters.extend(filters)

        conversations = frappe.get_all(
            "Messenger Conversation",
            filters=base_filters,
            fields=[
                "name",
                "sender_id",
                "last_message",
                "last_message_time",
                "platform",
                "block_chat",
                "status",
            ],
            order_by="last_message_time desc",
            limit=limit,
            start=offset,
        )

        if not conversations:
            return {
                "conversations": [],
                "user_profiles": {},
                "conversation_tags": {},
                "conversation_assignees": {},
                "unread_counts": {},
            }

        sender_ids = list(
            set([conv.sender_id for conv in conversations if conv.sender_id])
        )

        # Get user profiles
        user_profiles = {}
        if sender_ids:
            users = frappe.get_all(
                "Messenger User",
                filters=[["user_id", "in", sender_ids]],
                fields=["user_id", "username", "profile"],
            )
            user_profiles = {user.user_id: user for user in users}

        # Get conversation names
        conversation_names = [conv.name for conv in conversations]

        # Get all tags for conversations
        conversation_tags = {}
        for conv_name in conversation_names:
            conv_doc = frappe.get_doc("Messenger Conversation", conv_name)
            tags = []
            for row in conv_doc.tags:
                color = frappe.db.get_value("Messenger Tags", row.tag, "color")
                tags.append({"tag_name": row.tag, "color": color})
            conversation_tags[conv_name] = tags

        # Get all assignees for conversations
        conversation_assignees = {}
        todos = frappe.get_all(
            "ToDo",
            filters=[
                ["reference_type", "=", "Messenger Conversation"],
                ["reference_name", "in", conversation_names],
                ["status", "=", "Open"],
            ],
            fields=["reference_name", "allocated_to"],
        )

        # Group todos by conversation
        todos_by_conversation = {}
        for todo in todos:
            if todo.reference_name not in todos_by_conversation:
                todos_by_conversation[todo.reference_name] = []
            todos_by_conversation[todo.reference_name].append(todo.allocated_to)

        # Get user details for assignees
        all_assignee_ids = list(set([todo.allocated_to for todo in todos]))
        assignee_users = {}
        if all_assignee_ids:
            users = frappe.get_all(
                "User",
                filters=[["name", "in", all_assignee_ids]],
                fields=["name", "full_name", "user_image"],
            )
            assignee_users = {user.name: user for user in users}

        # Build assignees data
        for conv_name in conversation_names:
            assignee_ids = todos_by_conversation.get(conv_name, [])
            assignees = []
            for assignee_id in assignee_ids:
                user = assignee_users.get(assignee_id, {})
                assignees.append(
                    {
                        "name": assignee_id,
                        "image": user.get("user_image"),
                        "label": user.get("full_name") or assignee_id,
                    }
                )
            conversation_assignees[conv_name] = assignees

        # Get unread counts
        unread_counts = {}
        unread_data = frappe.get_all(
            "Messenger Message",
            filters=[
                ["conversation", "in", conversation_names],
                ["message_direction", "=", "Incoming"],
                ["is_read", "=", 0],
            ],
            fields=["conversation", "count(name) as unread_count"],
            group_by="conversation",
        )

        for item in unread_data:
            unread_counts[item.conversation] = item.unread_count

        # Add user profile data to conversations
        enhanced_conversations = []
        for conv in conversations:
            user_profile = user_profiles.get(conv.sender_id, {})
            enhanced_conversations.append(
                {
                    **conv,
                    "title": user_profile.get("username") or conv.sender_id,
                    "profile": user_profile.get("profile"),
                }
            )

        return {
            "conversations": enhanced_conversations,
            "user_profiles": user_profiles,
            "conversation_tags": conversation_tags,
            "conversation_assignees": conversation_assignees,
            "unread_counts": unread_counts,
        }

    except Exception as e:
        frappe.log_error("Get Conversations With Details Error", str(e))
        return None


@frappe.whitelist()
def get_cached_data():
    """Get cached data that doesn't change frequently."""
    try:
        all_tags = frappe.get_all(
            "Messenger Tags", fields=["tag_name", "color"], order_by="tag_name asc"
        )

        all_statuses = frappe.get_all(
            "Messenger Conversation Status", fields=["status"], order_by="status asc"
        )

        # Get helpdesk ticket creation flag
        helpdesk_enabled = False
        if frappe.db.exists("DocType", "Messenger Settings"):
            helpdesk_enabled = frappe.get_cached_value(
                "Messenger Settings",
                "Messenger Settings",
                "enable_helpdesk_ticket_creation",
            )

        return {
            "all_tags": all_tags,
            "all_statuses": [status.status for status in all_statuses],
            "helpdesk_enabled": helpdesk_enabled,
        }

    except Exception as e:
        frappe.log_error("Get Cached Data Error", str(e))
        return None


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