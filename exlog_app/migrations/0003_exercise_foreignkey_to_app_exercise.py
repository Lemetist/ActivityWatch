from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('exlog_app', '0002_alter_exercise_exercise_name_and_more'),
        ('app', '0003_exercise_ex_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exercise',
            name='exercise_name',
        ),
        migrations.AddField(
            model_name='exercise',
            name='exercise_ref',
            field=models.ForeignKey(
                to='app.Exercise',
                on_delete=django.db.models.deletion.CASCADE,
                verbose_name='Упражнение',
                null=False,
                default=1
            ),
        ),
    ]
