import json
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .form import PreferencesForm
from .models import PlayHistory, UserPreferences, UserProfile
from django.http import JsonResponse

def signup(request):
    registration_successful = False  # Default value

    if request.method == 'POST':
        # Retrieve form data from POST request
        username = request.POST.get('username1')
        email = request.POST.get('signup-email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validate form data
        if not username or not email or not password1 or not password2:
            messages.error(request, 'Please fill in all fields.')
            return redirect('/home')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('/home')

        # Create a new user
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            registration_successful = True  # Set to True if registration is successful
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'There was an error creating your account: {e}')
            return redirect('home')

    # Render the template with the registration status
    return render(request, 'home.html', {'registration_successful': registration_successful})

def user_song_history(request, username):
    user_obj = get_object_or_404(User, username=username)
    song_history = PlayHistory.objects.filter(user=user_obj).order_by('-date_played')  # newest songs first

    context = {
        'user_obj': user_obj,
        'song_history': song_history,
    }
    # print("data",context)
    return render(request, 'song_history.html', context)

def add_song_history(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        song_title = data.get('song_title')
        artist_name = data.get('artist_name')
        album_image = data.get('album_image')
        preview_url = data.get('preview_url')
    
        if not song_title or not artist_name:
            return JsonResponse({'status': 'error', 'message': 'Missing song details'}, status=400)
        
        PlayHistory.objects.create(
            user=request.user,
            song_title=song_title,
            artist_name=artist_name,
            album_image=album_image,
            preview_url = preview_url,
        )
        # print("Data with preview_url:", PlayHistory.objects.latest('timestamp'))  # Adjust based on your timestamp field
        return JsonResponse({'status': 'ok'})
    
    return JsonResponse({'status': 'ok', 'message': 'valid request'})

def preferences_view(request):
    user_preferences = None
    user_has_preferences = None

    if request.user.is_authenticated:
        try:
            user_preferences = UserPreferences.objects.get(user=request.user)
            # user_has_preferences = PreferencesForm(instance=user_preferences)
            user_has_preferences = None
        except UserPreferences.DoesNotExist:  
            if request.method == 'POST':
                user_has_preferences = PreferencesForm(request.POST)
                if user_has_preferences.is_valid():
                    preferences = user_has_preferences.save(commit=False)
                    preferences.user = request.user
                    preferences.save()
                    # return redirect('preferences_view')  # Redirect to avoid re-displaying form with errors
            else:
                user_has_preferences = PreferencesForm()
    print(user_has_preferences,"user")
    return user_has_preferences