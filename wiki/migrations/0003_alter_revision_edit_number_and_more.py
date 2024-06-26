# Generated by Django 4.0.1 on 2022-02-19 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0002_page_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='revision',
            name='edit_number',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddConstraint(
            model_name='revision',
            constraint=models.UniqueConstraint(fields=('parent', 'edit_number'), name='unique_edit_number'),
        ),
    ]
