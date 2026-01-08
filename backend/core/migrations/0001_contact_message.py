# Generated migration file for ContactMessage model

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(db_index=True, max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('subject', models.CharField(choices=[('general', 'General Inquiry'), ('order', 'Order Question'), ('shipping', 'Shipping Issue'), ('return', 'Return/Refund'), ('partnership', 'Partnership Opportunity'), ('other', 'Other')], db_index=True, max_length=20)),
                ('message', models.TextField()),
                ('status', models.CharField(choices=[('new', 'New'), ('reading', 'Reading'), ('replied', 'Replied'), ('closed', 'Closed')], db_index=True, default='new', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reply', models.TextField(blank=True, null=True)),
                ('replied_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Contact Message',
                'verbose_name_plural': 'Contact Messages',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='contactmessage',
            index=models.Index(fields=['email'], name='core_contactm_email_idx'),
        ),
        migrations.AddIndex(
            model_name='contactmessage',
            index=models.Index(fields=['status'], name='core_contactm_status_idx'),
        ),
        migrations.AddIndex(
            model_name='contactmessage',
            index=models.Index(fields=['created_at'], name='core_contactm_created_idx'),
        ),
    ]
