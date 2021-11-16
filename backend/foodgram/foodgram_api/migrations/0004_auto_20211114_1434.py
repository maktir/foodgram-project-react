# Generated by Django 3.1 on 2021-11-14 11:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram_api', '0003_auto_20211114_1358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carted_recipe', to='foodgram_api.recipe'),
        ),
    ]
