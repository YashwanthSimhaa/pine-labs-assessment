def derive_status(current_status, event_type):
    if event_type == "payment_failed":
        return "failed"
    if event_type == "settled":
        return "settled"
    if event_type == "payment_processed":
        return "processed"
    return current_status