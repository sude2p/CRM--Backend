# Generated by Django 5.1 on 2024-10-15 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "contactmanagement",
            "0005_alter_contact_email_alter_contact_phone_mobile_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="contact",
            name="email",
            field=models.EmailField(max_length=254),
        ),
    ]
