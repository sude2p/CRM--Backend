# Generated by Django 5.1 on 2024-09-09 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "contactmanagement",
            "0002_company_remove_contact_organization_contact_source_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="contact",
            name="company",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.DeleteModel(
            name="Company",
        ),
    ]
