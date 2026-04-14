from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, RadioField, TimeField
from wtforms.validators import Optional, Regexp, ValidationError
import re

class WorkflowForm(FlaskForm):
    """Workflow form for Page 2"""
    
    # Time input (optional)
    final_block_time = TimeField('Final Block Time', 
        validators=[Optional()],
        format='%H:%M'
    )
    
    # PT Link fields
    baked_ihcs_pt_link = BooleanField('Baked IHCs PT Link')
    ihcs_in_pt_link = BooleanField('IHCs in PT Link')

    # DAKO fields
    non_baked_ihc = BooleanField('Non-Baked IHC')
    ihcs_in_buffer_wash = BooleanField('IHCs in Buffer Wash')

    # Pathologist Requests fields
    pathologist_requests_status = RadioField('Pathologist Requests Status',
        choices=[('completed', 'All Completed'), ('pending', 'Pending/Incomplete')],
        validators=[Optional()]
    )
    request_source_email = BooleanField('Email')
    request_source_orchard = BooleanField('Orchard')
    request_source_send_out = BooleanField('Send Out')

    # HER2 fields
    in_progress_her2 = BooleanField('In Progress HER2')
    
    # Special Stains fields
    upfront_special_stains = RadioField('Upfront Special Stains',
        choices=[('completed', 'Completed'), ('incomplete', 'Incomplete')],
        validators=[Optional()]
    )

    # Task Status fields
    peloris_maintenance = RadioField('Peloris Maintenance',
        choices=[('completed', 'Completed'), ('incomplete', 'Incomplete')],
        validators=[Optional()]
    )
    
    def validate_final_block_time(self, field):
        """Validate time format if provided"""
        if field.data:
            # Additional validation can be added here if needed
            pass