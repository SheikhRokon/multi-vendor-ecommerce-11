# Generated by Django 4.2.3 on 2023-10-04 04:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('other_vendors', '0002_vendorinformation_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendorinformation',
            name='vendor_image',
            field=models.ImageField(blank=True, null=True, upload_to='vendor_image/'),
        ),
    ]
