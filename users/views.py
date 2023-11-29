import json
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .form import AvatarForm
from .models import PlayHistory, UserProfile
from django.http import JsonResponse

def password_reset_done_with_message(request):
    messages.success(request, 'Password reset email has been sent!')
    return render(request, 'password_reset_done_with_message.html')

def signup(request):
    if request.method == 'POST':
        # Retrieve form data from POST request
        username = request.POST.get('username1')
        email = request.POST.get('signup-email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validate form data
        if not username or not email or not password1 or not password2:
            messages.error(request, 'Please fill in all fields.')
            return redirect('home')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('home')

        # Create a new user
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'There was an error creating your account: {e}')
            return redirect('home')

    # If the request is not a POST request, render the signup page
    return render(request, 'home.html')

def send_welcome_email(recipient_email):
    send_mail(
        'Welcome to Our Site',
        'Thank you for registering with us. We hope you enjoy our services.',
        'webmaster@example.com',  # This should be your sending email
        [recipient_email],
        fail_silently=False,  # This will raise an exception if there's an issue
    )

def user_song_history(request, username):
    user_obj = get_object_or_404(User, username=username)
    song_history = PlayHistory.objects.filter(user=user_obj).order_by('-date_played')  # newest songs first

    context = {
        'user_obj': user_obj,
        'song_history': song_history,
    }
    print("data",context)
    return render(request, 'song_history.html', context)

def add_song_history(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        song_title = data.get('song_title')
        artist_name = data.get('artist_name')
        album_image = data.get('album_image')
    
        if not song_title or not artist_name:
            return JsonResponse({'status': 'error', 'message': 'Missing song details'}, status=400)
        
        PlayHistory.objects.create(
            user=request.user,
            song_title=song_title,
            artist_name=artist_name,
            album_image=album_image,
        )
        print("data",PlayHistory);
        return JsonResponse({'status': 'ok'})
    
    return JsonResponse({'status': 'ok', 'message': 'valid request'})

def upload_avatar(request):
    if request.method == 'POST':
        form = AvatarForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.avatar = form.cleaned_data['avatar']
            user_profile.save()
            return redirect('profile')
    else:
        form = AvatarForm()
    return render(request, 'song_history.html', {'form': form})