# Generated by Django 3.2.4 on 2021-07-05 20:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Explanation',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('text', 'Text'), ('code', 'Code'), ('image', 'Image')], max_length=32)),
                ('pos', models.IntegerField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=128)),
                ('content', models.CharField(blank=True, max_length=4096)),
            ],
        ),
        migrations.CreateModel(
            name='HowTo',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, max_length=128)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('description', models.CharField(blank=True, max_length=1024)),
            ],
            options={
                'verbose_name': "How To'",
            },
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, max_length=128)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('description', models.CharField(blank=True, max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='Super',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pos', models.IntegerField()),
                ('step_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='substep', to='api.step')),
                ('super_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='superstep', to='api.step')),
            ],
            options={
                'verbose_name': 'Superstep',
            },
        ),
        migrations.CreateModel(
            name='StepUriId',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('uri_id', models.CharField(max_length=8)),
                ('step_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.step')),
            ],
            options={
                'verbose_name': "Step Uri Id'",
            },
        ),
        migrations.CreateModel(
            name='HowToUriId',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('uri_id', models.CharField(max_length=8)),
                ('how_to_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.howto')),
            ],
            options={
                'verbose_name': "How To Uri Id'",
            },
        ),
        migrations.CreateModel(
            name='HowToStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pos', models.IntegerField()),
                ('how_to_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='how_to', to='api.howto')),
                ('step_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='step', to='api.step')),
            ],
            options={
                'verbose_name': "How To's linked Step",
            },
        ),
        migrations.CreateModel(
            name='ExplanationUriId',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('uri_id', models.CharField(max_length=8)),
                ('explanation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.explanation')),
            ],
        ),
        migrations.AddField(
            model_name='explanation',
            name='step',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.step'),
        ),
    ]
