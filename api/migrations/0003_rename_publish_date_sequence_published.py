# Generated by Django 4.0.6 on 2022-07-06 19:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_linkedstep_pos'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sequence',
            old_name='publish_date',
            new_name='published',
        ),
    ]