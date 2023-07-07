from drf_extra_fields.fields import Base64FileField
import io
import PyPDF2
import logging


class PDFBase64File(Base64FileField):
    ALLOWED_TYPES = ['pdf']

    def get_file_extension(self, filename, decoded_file):
        try:
            PyPDF2.PdfFileReader(io.BytesIO(decoded_file))
        except Exception as e:
            print(e)

                
        else:
            return 'pdf'