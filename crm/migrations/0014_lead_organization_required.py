import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0013_backfill_lead_organization'),
        ('accounts', '0002_backfill_organizations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='leads',
                to='accounts.organization',
            ),
        ),
    ]
