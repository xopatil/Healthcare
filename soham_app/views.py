from datetime import date, datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
import jwt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.forms.models import model_to_dict
from soham_app.models import Patient, Doctor, Appointment, Prescription
from soham_app.send_email import send_html_email
from django.db.models import Count, Func, Sum
from django.db import models

doc_reg_numbers = [166906, 317736, 348954, 748817, 259517, 445414, 209381, 544359, 791161, 241998, 368957, 733847,
                   985625, 866768, 367826]


# Create your views here.
def register_view(request):
    return render(request, 'onboarding/registration.html')


def forget_password(request):
    if request.method == "GET":
        return render(request, 'onboarding/forget_password.html')
    if request.method == "POST":
        email = request.POST.get('emailReset')
        doctor_count = Doctor.objects.filter(email=email).count()
        if doctor_count == 0:
            patient_count = Patient.objects.filter(email=email).count()
            if patient_count == 0:
                messages.error(request, 'Email Id Does Not Exist')
                return redirect('forget_password')
            else:
                send_html_email(email)
                messages.success(request, 'Password Reset Link Has Been Sent to your email, Please Check')
                return redirect('forget_password')

        else:
            send_html_email(email)
            messages.success(request, 'Password Reset Link Has Been Sent to your email, Please Check')
            return redirect('forget_password')
    return redirect('login')


def home(request):
    return render(request, 'index.html')


def login_view(request):
    return render(request, 'onboarding/login.html')


def doctor_register_api(request):
    if request.method == 'POST':
        registration_number = int(request.POST.get('doctorRegNumber'))
        if registration_number not in doc_reg_numbers:
            messages.error(request, 'Invalid Doctors Registration Number')
            return redirect('/register/?tab=doctor')
        # Extracting the data from the POST request
        doctor = Doctor(
            name=request.POST.get('doctorName'),
            registration_number=request.POST.get('doctorRegNumber'),
            mobile_number=request.POST.get('doctorMobile'),
            address=request.POST.get('doctorAddress'),
            email=request.POST.get('doctorEmail'),
            password=make_password(request.POST.get('doctorPassword')),
            qualification=request.POST.get('qualification'),
            gender=request.POST.get('doctorGender'),
            date_of_birth=request.POST.get('doctorDOB'),
            age=int(request.POST.get('doctorAge'))  # Convert the age from string to int
        )

        doctor.save()

        # Redirecting to another view or page after saving (adjust as necessary)
        messages.success(request, 'Registration Successful, Please Login')
        return redirect('/login/?tab=doctorLogin')
    return redirect('login')


def patient_register_api(request):
    if request.method == "POST":
        name = request.POST.get('patientName')
        age = request.POST.get('patientAge')
        blood_group = request.POST.get('bloodGroup')
        address = request.POST.get('patientAddress')
        gender = request.POST.get('gender')
        mobile_number = request.POST.get('mobileNumber')
        email = request.POST.get('patientEmail')
        password = request.POST.get('patientPassword')
        dob = request.POST.get('dob')
        medical_history = request.POST.get('medicalHistory', "")  # Defaulting to empty string if not present

        # Creating a new instance of the Patient model
        patient = Patient(
            name=name,
            age=age,
            blood_group=blood_group,
            address=address,
            gender=gender,
            mobile_number=mobile_number,
            email=email,
            password=make_password(password),
            date_of_birth=dob,
            medical_history=medical_history
        )

        # Saving the instance to the database
        patient.save()

        # Redirecting to another view or page after saving (adjust as necessary)
        messages.success(request, 'Your data has been saved successfully!')
        return redirect('login')
    return redirect('login')


def login_patient(request):
    if request.method == "POST":

        email = request.POST.get('patientEmailLogin')
        password = request.POST.get('patientPasswordLogin')

        email_count = Patient.objects.filter(email=email).count()
        if email_count == 0:
            messages.error(request, 'Email Id Does Not Exist')
            return redirect('login')

        patient = Patient.objects.get(email=email)
        password_check = check_password(password, patient.password)
        if password_check:
            messages.success(request, 'Login Successful')
            patient_dict = model_to_dict(patient)
            patient_dict["date_of_birth"] = patient.date_of_birth.isoformat() if patient.date_of_birth else None
            request.session["patient_session"] = patient_dict
            return redirect('view_appointment')
        else:
            messages.error(request, 'Incorrect Password')
            return redirect('login')
    return redirect('login')


def login_doctor(request):
    if request.method == "POST":

        email = request.POST.get('doctorEmailLogin')
        password = request.POST.get('doctorPasswordLogin')

        email_count = Doctor.objects.filter(email=email).count()
        if email_count == 0:
            messages.error(request, 'Email Id Does Not Exist')
            return redirect('/login/?tab=doctorLogin')

        doctor = Doctor.objects.get(email=email)
        password_check = check_password(password, doctor.password)
        if password_check:
            messages.success(request, 'Login Successful')
            doctor_dict = model_to_dict(doctor)
            request.session["doctor_session"] = doctor_dict
            doctor_dict["date_of_birth"] = doctor.date_of_birth.isoformat() if doctor.date_of_birth else None
            return redirect('doc_appointments')
        else:
            messages.error(request, 'Incorrect Password')
            return redirect('/login/?tab=doctorLogin')
    return redirect('login')


def reset_password(request, token):
    if request.method == "GET":
        try:
            jwt.decode(token, "soham_pass", algorithms=["HS256"])
            return render(request, 'onboarding/reset_password.html', {"token": token})
        except:
            return render(request, 'onboarding/success_msg.html')
    if request.method == "POST":
        data = jwt.decode(token, "soham_pass", algorithms=["HS256"])
        email = data["email"]
        new_password = request.POST.get('newPassword')
        doctorCount = Doctor.objects.filter(email=email).count()
        if doctorCount == 0:
            patient = Patient.objects.get(email=email)
            patient.password = make_password(new_password)
            patient.save()
            messages.success(request, 'Password Reset Successful, Please Login')
            return redirect('/login/')
        else:
            doctor = Doctor.objects.get(email=email)
            doctor.password = make_password(new_password)
            doctor.save()
            messages.success(request, 'Password Reset Successful, Please Login')
            return redirect('/login/?tab=doctorLogin')
    else:
        return redirect('login')


def book_appointment(request):
    if request.method == "GET":
        if "patient_session" in request.session:
            name = request.session['patient_session']['name']
            doctors_obj = Doctor.objects.all()
            doctors = [doc for doc in doctors_obj]
            return render(request, 'patient/book_appointment.html', {"data": doctors, 'name': name})
    if request.method == "POST":
        if "patient_session" in request.session:
            patient = request.session["patient_session"]
            patient_email = patient["email"]
            doc = request.POST.get('doctorSelect')
            date = request.POST.get('appointmentDate')
            time = request.POST.get('timeSlot')

            booking_data = {
                "doc": doc,
                "date": date,
                "time": time,
                "patient_email": patient_email
            }

            request.session["booking_data"] = booking_data
            return redirect("payment")
    else:
        return redirect('login')


def has_time_passed(date, time_range):
    # Convert end time of time range to 24-hour format
    end_time_str = time_range.split('-')[1]
    hour_24 = int(end_time_str[:-2]) + (12 if "PM" in end_time_str else 0)
    # Create a datetime object for the end time on the given date
    end_datetime = datetime.combine(date, datetime.min.time().replace(hour=hour_24 % 24))

    # Compare to current datetime
    return datetime.now() > end_datetime


@api_view(["GET"])
def get_available_times(request):
    if request.method == "GET":
        global output_list
        timings = [
            "9AM-10AM",
            "10AM-11AM",
            "11AM-12PM",
            "12PM-1PM",
            "1PM-2PM",
            "2PM-3PM",
            "3PM-4PM",
            "4PM-5PM"
        ]

        doctor_id = request.query_params.get('doctor_id')
        doctor_date = request.query_params.get('date')
        doc = Doctor.objects.get(id=doctor_id)
        appointments = Appointment.objects.filter(doctor=doc, date=doctor_date).count()
        if appointments != 0:
            temp_list = []
            appointments = Appointment.objects.filter(doctor=doc, date=doctor_date)
            for i in appointments:
                temp_list.append(i.time)
                output_list = [item for item in timings if item not in temp_list]
            return Response(data={"available_times": output_list})
        else:
            return Response(data={"available_times": timings})
    else:
        return redirect('login')


def payment(request):
    if request.method == "GET":
        if "booking_data" in request.session and "patient_session" in request.session:
            booking_data = request.session["booking_data"]
            doc = Doctor.objects.get(id=booking_data["doc"])
            doc_name = doc.name
            date = booking_data["date"]
            time = booking_data["time"]
            return render(request, "payment/payment_page.html", {"name": doc_name, "date": date, "time": time})
    if request.method == "POST":
        if "booking_data" in request.session and "patient_session" in request.session:
            booking_data = request.session["booking_data"]
            doc_obj = Doctor.objects.get(id=booking_data['doc'])
            patient = Patient.objects.get(email=booking_data["patient_email"])
            date = booking_data["date"]
            time = booking_data["time"]
            appointment = Appointment(
                patient=patient,
                doctor=doc_obj,
                date=date,  # Example date
                time=time,  # Example time
                fees_paid=True,
                amount_paid=500  # Example amount
            )
            appointment.save()
            del request.session["booking_data"]
            messages.success(request, 'Appointment Booked Successfully')
            return redirect('view_appointment')
    else:
        return redirect('login')


def view_appointments(request):
    if "patient_session" in request.session:
        patient_data = request.session["patient_session"]
        name = patient_data['name']
        patient = Patient.objects.get(email=patient_data["email"])
        appointments = Appointment.objects.filter(patient=patient)

        today = date.today()
        # Split appointments into future and past based on date and time
        future_appointments = [appointment for appointment in appointments if appointment.date > today or (
                appointment.date == today and not has_time_passed(appointment.date, appointment.time))]
        past_appointments = [appointment for appointment in appointments if not appointment in future_appointments]

        # Convert the filtered appointments into lists of dictionaries
        future_appointments_list = sorted(
            [
                {
                    'appointment_id': str(appointment.appointment_id),
                    'doctor': appointment.doctor.name,
                    'date': appointment.date,
                    'time': appointment.time
                }
                for appointment in future_appointments
            ],
            key=lambda x: (x['date'], time_to_sortable_value(x['time']))
        )

        past_appointments_list = sorted(
            [
                {
                    'appointment_id': str(appointment.appointment_id),
                    'doctor': appointment.doctor.name,
                    'date': appointment.date,
                    'time': appointment.time
                }
                for appointment in past_appointments
            ],
            key=lambda x: (x['date'], time_to_sortable_value(x['time'])),
            reverse=True
        )

        fal_new_structure = {}

        for appointment in future_appointments_list:
            doctor = appointment['doctor']
            if doctor in fal_new_structure:
                fal_new_structure[doctor]['appointments'].append({
                    'appointment_id': appointment['appointment_id'],
                    'date': appointment['date'],
                    'time': appointment['time']
                })
            else:
                fal_new_structure[doctor] = {
                    'appointments': [{
                        'appointment_id': appointment['appointment_id'],
                        'date': appointment['date'],
                        'time': appointment['time']
                    }]
                }

        # Convert the dictionary to a list of dictionaries
        fal_final_list = [{'doctor': key, **value} for key, value in fal_new_structure.items()]

        pal_new_structure = {}

        for appointment in past_appointments_list:
            doctor = appointment['doctor']
            if doctor in pal_new_structure:
                pal_new_structure[doctor]['appointments'].append({
                    'appointment_id': appointment['appointment_id'],
                    'date': appointment['date'],
                    'time': appointment['time']
                })
            else:
                pal_new_structure[doctor] = {
                    'appointments': [{
                        'appointment_id': appointment['appointment_id'],
                        'date': appointment['date'],
                        'time': appointment['time']
                    }]
                }

        # Convert the dictionary to a list of dictionaries
        pal_final_list = [{'doctor': key, **value} for key, value in pal_new_structure.items()]

        return render(request, 'patient/view_appointments.html',
                      {"future": fal_final_list, "past": pal_final_list, 'name': name})
    else:
        return redirect('login')


def view_profile(request):
    if "patient_session" in request.session:
        patient_data = request.session["patient_session"]
        return render(request, 'patient/patient_profile.html', patient_data)
    else:
        return redirect('login')


def time_to_sortable_value(time_str):
    # Convert start time of time range to 24-hour format
    start_time_str = time_str.split('-')[0]
    hour_24 = int(start_time_str[:-2]) + (12 if "PM" in start_time_str and not "12" in start_time_str else 0)
    return hour_24


def doc_appointments(request):
    if "doctor_session" in request.session:
        doctor_data = request.session["doctor_session"]
        name = doctor_data['name']
        doctor = Doctor.objects.get(email=doctor_data["email"])
        appointments = Appointment.objects.filter(doctor=doctor)

        # Inside doc_appointments function:

        today = date.today()

        # Split appointments into future and past based on date and time
        future_appointments = [appointment for appointment in appointments if appointment.date > today or (
                appointment.date == today and not has_time_passed(appointment.date, appointment.time))]
        past_appointments = [appointment for appointment in appointments if not appointment in future_appointments]

        future_appointments_list = sorted(
            [
                {
                    'patient': appointment.patient.name,
                    'id': appointment.patient.id,
                    'date': appointment.date,
                    'time': appointment.time
                }
                for appointment in future_appointments
            ],
            key=lambda x: (x['date'], time_to_sortable_value(x['time']))
        )

        past_appointments_list = sorted(
            [
                {
                    'appointment_id': str(appointment.appointment_id),
                    'patient': appointment.patient.name,
                    'id': appointment.patient.id,
                    'date': appointment.date,
                    'time': appointment.time
                }
                for appointment in past_appointments
            ],
            key=lambda x: (x['date'], time_to_sortable_value(x['time'])),
            reverse=True
        )

        return render(request, "doctor/view_appointments.html",
                      {"future": future_appointments_list, "past": past_appointments_list, 'name': name})
    else:
        return redirect('login')


def doctor_profile(request):
    if "doctor_session" in request.session:
        doctor_data = request.session["doctor_session"]
        return render(request, 'doctor/doctor_profile.html', doctor_data)
    else:
        return redirect('login')


def pat_doc_profile(request, patient_id):
    if "doctor_session" in request.session:
        doc_name = request.session['doctor_session']
        doc_name = doc_name['name']
        patient = Patient.objects.get(id=patient_id)
        patient_dict = model_to_dict(patient)
        patient_dict["date_of_birth"] = patient.date_of_birth.isoformat() if patient.date_of_birth else None
        patient_dict['doc_name'] = doc_name
        return render(request, 'doctor/pat_doc_profile.html', patient_dict)
    else:
        return redirect('login')


def cancel_appointment(request, uuid_string):
    if "patient_session" in request.session:
        appointment = Appointment.objects.get(appointment_id=uuid_string)
        appointment.delete()
        messages.info(request, 'Appointment Cancelled Successfully')
        return redirect("view_appointment")
    else:
        return redirect('login')


def write_prescription(request, uuid_str):
    if request.method == "GET":
        if "doctor_session" in request.session:
            appointment = Appointment.objects.get(appointment_id=uuid_str)
            data = {
                'uuid_str': appointment.appointment_id,
                'patient': appointment.patient.name,
                'doctor': appointment.doctor.name,
                'date': appointment.date,
                'time': appointment.time
            }

            app = Prescription.objects.filter(appointment=appointment).count()
            if app != 0:
                app = Prescription.objects.get(appointment=appointment)
                data["prescription"] = app.prescription
            return render(request, 'doctor/write_prescription.html', data)
    if request.method == "POST":
        if "doctor_session" in request.session:
            appointment = Appointment.objects.get(appointment_id=uuid_str)
            prescription = request.POST.get("special_instructions")

            pes_count = Prescription.objects.filter(appointment=appointment).count()
            if pes_count == 0:
                pes = Prescription(
                    appointment=appointment,
                    prescription=prescription
                )
                pes.save()
            else:
                pes = Prescription.objects.get(appointment=appointment)
                pes.prescription = prescription
                pes.save()
            messages.success(request, "Prescription Saved Successfully")
            return redirect('doc_appointments')
    else:
        return redirect('login')


def view_prescription(request, uuid_str):
    if request.method == "GET":
        if "patient_session" in request.session:
            appointment = Appointment.objects.get(appointment_id=uuid_str)
            pes_count = Prescription.objects.filter(appointment=appointment).count()
            if pes_count == 0:
                data = {
                    "patient": appointment.patient.name,
                    "doctor": appointment.doctor.name,
                    "date": appointment.date,
                    "time": appointment.time,
                    "prescription": "Not Available / Not Yet Updated By Doctor"
                }
            else:
                pes = Prescription.objects.get(appointment=appointment)
                data = {
                    "patient": appointment.patient.name,
                    "doctor": appointment.doctor.name,
                    "date": appointment.date,
                    "time": appointment.time,
                    "prescription": pes.prescription
                }

            return render(request, 'patient/view_prescription.html', data)
    else:
        return redirect('login')


def logout(request):
    if "doctor_session" in request.session:
        del request.session["doctor_session"]
        messages.success(request, 'Logout Successful')
        return redirect('/login/?tab=doctorLogin')
    if "patient_session" in request.session:
        del request.session["patient_session"]
        messages.success(request, 'Logout Successful')
        return redirect('login')
    else:
        return redirect('login')


class ExtractMonth(Func):
    function = 'EXTRACT'
    template = '%(function)s(MONTH from %(expressions)s)'
    output_field = models.IntegerField()


def analytics(request):
    if "doctor_session" in request.session:
        doctor_data = request.session['doctor_session']
        name = doctor_data['name']
        doc = Doctor.objects.get(email=doctor_data['email'])
        temp_var = Appointment.objects.filter(doctor=doc)
        monthly_counts = (
            temp_var.annotate(month=ExtractMonth('date'))
            .values('month')
            .annotate(patient_count=Count('patient'))
            .order_by('month')
        )

        monthly_sums = (
            temp_var.annotate(month=ExtractMonth('date'))
            .values('month')
            .annotate(total_amount=Sum('amount_paid'))
            .order_by('month')
        )

        monthly_data = {item['month']: item['patient_count'] for item in monthly_counts}

        # Get the counts for each month
        patient_counts_per_month = [monthly_data.get(month, 0) for month in range(1, 13)]

        monthly_data = {item['month']: item['total_amount'] for item in monthly_sums}

        # Get the sums for each month
        amount_sums_per_month = [monthly_data.get(month, 0) for month in range(1, 13)]

        return render(request, 'doctor/analytics.html',
                      {"pat_count": patient_counts_per_month, "revenue": amount_sums_per_month, "name":name})
