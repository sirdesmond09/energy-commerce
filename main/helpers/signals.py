from django import dispatch

payment_approved = dispatch.Signal(providing_args=["payment", 'user'])