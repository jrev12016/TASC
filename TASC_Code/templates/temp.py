def oldStudents():
    
    TAs = User.query.filter_by(user_type='TA').all()
    TA_choices = [(ta.id, ta.display_name) for ta in TAs]

    # Form to schedule an appointment
    form = MakeAppt()
    form.TA.choices = TA_choices
    if form.validate_on_submit():
        TA = form.TA.data
        day = form.day.data
        list = []
        list.append((('9:00 a.m.', Appointment.query.filter_by(TA_id=TA, day=day).first().nine)))
        list.append((('10:00 a.m.', Appointment.query.filter_by(TA_id=TA, day=day).first().ten)))
        list.append((('11:00 a.m.', Appointment.query.filter_by(TA_id=TA, day=day).first().eleven)))
        list.append((('12:00 a.m.', Appointment.query.filter_by(TA_id=TA, day=day).first().twelve)))
        list.append((('1:00 p.m.', Appointment.query.filter_by(TA_id=TA, day=day).first().one)))
        list.append((('2:00 p.m.', Appointment.query.filter_by(TA_id=TA, day=day).first().two)))
        list.append((('3:00 p.m.', Appointment.query.filter_by(TA_id=TA, day=day).first().three)))
        list.append((('4:00 p.m.', Appointment.query.filter_by(TA_id=TA, day=day).first().four)))
        
        # Only display available times
        list_available = []
        for times in list:
            time, conditional = times
            if conditional:
                list_available.append(time)
            
        return render_template('student.html', TA=TA, day=day, list_available=list_available)

    return render_template('student.html', form=form)
    