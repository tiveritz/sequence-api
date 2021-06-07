from django.db import models


class HowTo(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length = 128, blank = True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length = 1024, blank = True)

    #def uri_id(self):
    #    return HowToUriId.objects.get(pk = self.id)
    
    @property
    def uri_id(self):
        return HowToUriId.objects.get(how_to_id=self)

    def __str__(self):
        return f'{self.title}'
    
    class Meta:
        verbose_name = 'How To\''


class HowToUriId(models.Model):
    id = models.BigAutoField(primary_key=True)
    how_to_id = models.OneToOneField(
        HowTo,
        on_delete = models.CASCADE
        )
    uri_id = models.CharField(max_length = 8)

    def __str__(self):
        return f'{self.uri_id}'

    class Meta:
        verbose_name = 'How To Uri Id\''
