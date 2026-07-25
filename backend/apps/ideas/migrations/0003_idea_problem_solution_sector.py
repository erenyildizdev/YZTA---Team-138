from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ideas", "0002_validationroadmap"),
    ]

    operations = [
        migrations.AddField(
            model_name="idea",
            name="problem",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="idea",
            name="solution",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="idea",
            name="sector",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
    ]
