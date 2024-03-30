from django.urls import path

from soham_app import views

urlpatterns = [
    path('register/', views.register_view, name="register"),
    path('login/', views.login_view, name="login"),
    path('signup-doctor/', views.doctor_register_api, name="register-doctor"),
    path('signup-patient/', views.patient_register_api, name="register-patient"),
    path('login-patient/', views.login_patient, name="login_patient"),
    path('login-doctor/', views.login_doctor, name="login_doctor"),
    path('forget-password/', views.forget_password, name="forget_password"),
    path('', views.home, name="home"),
    path('reset-password/<str:token>', views.reset_password, name="reset_password"),
    path('book-appointment/', views.book_appointment, name="book_appointment"),
    path('view-appointments/', views.view_appointments, name="view_appointment"),
    path('get-available-times/', views.get_available_times, name="get-available-times"),
    path('payment/', views.payment, name="payment"),
    path('profile/', views.view_profile, name="view_profile"),
    path('doctor-appointments/', views.doc_appointments, name="doc_appointments"),
    path('doctor-profile/', views.doctor_profile, name="doctor_profile"),
    path('patient/<str:patient_id>', views.pat_doc_profile, name="pat_doc_profile"),
    path('cancel/<str:uuid_string>', views.cancel_appointment, name="cancel_appointment"),
    path('logout/', views.logout, name="logout"),
    path('prescription/<str:uuid_str>', views.write_prescription, name="write_prescription"),
    path('view-prescription/<str:uuid_str>', views.view_prescription, name="write_prescription"),
    path('analytics/', views.analytics, name="analytics")
]
