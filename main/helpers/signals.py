from django import dispatch

payment_approved = dispatch.Signal('user')

password_changed = dispatch.Signal("user_data")

post_store_delete = dispatch.Signal("vendor")

payment_declined = dispatch.Signal("user")

vendor_created = dispatch.Signal("vendor")
