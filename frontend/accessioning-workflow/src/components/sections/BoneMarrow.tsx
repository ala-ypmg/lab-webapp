from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, RadioField, TimeField
from wtforms.validators import Optional

STATUS_CHOICES = [('done', 'Done'), ('pending', 'Pending'), ('na', 'N/A')]

class WorkflowForm(FlaskForm):
    """Workflow form for Page 2"""

    # Time input (optional)
    final_block_time = TimeField('Final Block Time',
        validators=[Optional()],
        format='%H:%M'
    )

    # PT Link fields
    baked_ihcs_pt_link = RadioField('Baked IHCs', choices=STATUS_CHOICES, validators=[Optional()])
    ihcs_in_pt_link    = RadioField('IHCs in PT Link', choices=STATUS_CHOICES, validators=[Optional()])

    # DAKO fields
    non_baked_ihc       = RadioField('Non-baked IHC', choices=STATUS_CHOICES, validators=[Optional()])
    ihcs_in_buffer_wash = RadioField('IHCs in Buffer Wash', choices=STATUS_CHOICES, validators=[Optional()])

    # Pathologist Requests fields
    pathologist_requests_status = RadioField('Pathologist Requests',
        choices=STATUS_CHOICES, validators=[Optional()])
    request_source_email   = BooleanField('Email')
    request_source_orchard = BooleanField('Orchard')
    request_source_send_out = BooleanField('Send Out')

    # HER2 field
    in_progress_her2 = RadioField('HER2', choices=STATUS_CHOICES, validators=[Optional()])

    # Special Stains field
    upfront_special_stains = RadioField('Special Stains',
        choices=STATUS_CHOICES, validators=[Optional()])

    # Peloris Maintenance field
    peloris_maintenance = RadioField('Peloris Maintenance',
        choices=STATUS_CHOICES, validators=[Optional()])
