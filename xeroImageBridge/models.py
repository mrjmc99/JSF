from django.db import models
from django.utils.text import slugify

class AppPermissions(models.Model):
    class Meta:
        permissions = [
            ("use_xeroImageBridge", "Can use Xero Image Bridge"),
        ]

class XeroConfig(models.Model):
    xero_user = models.CharField(max_length=255)
    xero_password = models.CharField(max_length=255)
    xero_server = models.CharField(max_length=255)
    xero_domain = models.CharField(max_length=255, default="agility")
    query_constraints = models.CharField(max_length=255, default="PatientID={patient_id}")
    display_vars = models.CharField(max_length=255,
                                             default="theme=ahsxero&PatientID={patient_id}&AccessionNumber={accession_number}")
    ticket_duration = models.IntegerField(default=1800)
    xero_server_slug = models.SlugField(max_length=255, blank=True, unique=True)

    def save(self, *args, **kwargs):
        self.xero_server_slug = slugify(self.xero_server)
        super(XeroConfig, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.xero_server} - {self.xero_user}"