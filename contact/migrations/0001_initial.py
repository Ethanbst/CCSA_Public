# Generated by Django 5.1.7 on 2025-05-20 06:28

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ContactEmail",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(max_length=254, verbose_name="Email")),
                ("is_active", models.BooleanField(default=True, verbose_name="Actif")),
            ],
            options={
                "verbose_name": "Contact Email",
                "verbose_name_plural": "Contact Emails",
            },
        ),
    ]
