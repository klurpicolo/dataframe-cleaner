from django.db import models
from django.utils.translation import gettext_lazy as _

from model_utils.fields import AutoCreatedField, AutoLastModifiedField


class IndexedTimeStampedModel(models.Model):
    created = AutoCreatedField(_("created"), db_index=True)
    modified = AutoLastModifiedField(_("modified"), db_index=True)

    class Meta:
        abstract = True

class DataFrameStorage(models.Model):
    dataframe_id = models.CharField(_("dataframe ID"), max_length=100, unique=True)
    version = models.CharField(_("version"), max_length=50)
    created = AutoCreatedField(_("created"), db_index=True)
    modified = AutoLastModifiedField(_("modified"), db_index=True)
    data = models.JSONField(_("data"), default=dict)

    class Meta:
        verbose_name = _("Data Frame Storage")
        verbose_name_plural = _("Data Frame Storages")

    def __str__(self):
        return f"{self.dataframe_id} (Version: {self.version})"


class DataFrameStorage2:
    dataframe_id: str
    version: str
    data: str

    def __str__(self):
        return f"{self.dataframe_id} (Version: {self.version})"
