from django import dispatch

payment_approved = dispatch.Signal('user')

password_changed = dispatch.Signal("user_data")
