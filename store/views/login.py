from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth.hashers import check_password
from store.models.customer import Customer
from django.views import View
from django.core.cache import cache
from datetime import datetime, timedelta
from django.contrib import messages

class Login(View):
    return_url = None

    def get(self, request):
        Login.return_url = request.GET.get('return_url')
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_customer_by_email(email)
        error_message = None

        # Get the number of failed attempts from the cache
        failed_attempts = cache.get('failed_attempts_{}'.format(email), 0)
        last_attempt_time = cache.get('last_attempt_time_{}'.format(email))

        # Check if the user has failed to login more than 3 times in the last 30 seconds
        if failed_attempts >= 3 and last_attempt_time and (datetime.now() - last_attempt_time).total_seconds() < 30:
            error_message = 'Too many failed login attempts. Please try again after 30 seconds.'
            messages.add_message(request, messages.ERROR, 'Too many failed login attempts. Please try again after 30 seconds.')
        elif customer:
            flag = check_password(password, customer.password)
            if flag:
                # If login is successful, reset the failed attempts
                cache.set('failed_attempts_{}'.format(email), 0)
                request.session['customer'] = customer.id

                if Login.return_url:
                    return HttpResponseRedirect(Login.return_url)
                else:
                    Login.return_url = None
                    return redirect('homepage')
            else:
                error_message = 'The Email and Password does not match!'
                # Increment the number of failed attempts
                cache.set('failed_attempts_{}'.format(email), failed_attempts + 1)
                # Update the time of the last attempt
                cache.set('last_attempt_time_{}'.format(email), datetime.now())
        else:
            error_message = 'The Email and Password does not match!'
            # Increment the number of failed attempts
            cache.set('failed_attempts_{}'.format(email), failed_attempts + 1)
            # Update the time of the last attempt
            cache.set('last_attempt_time_{}'.format(email), datetime.now())

        # Calculate countdown value to pass to template
        countdown_value = 30 - int((datetime.now() - last_attempt_time).total_seconds()) if last_attempt_time else 0

        return render(request, 'login.html', {'error': error_message, 'entered_email': email, 'countdown_value': countdown_value})

def logout(request):
    request.session.clear()
    return redirect('login')
